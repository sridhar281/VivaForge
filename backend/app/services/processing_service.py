"""
This is the function that runs in the background after a user hits
"process" on an upload. It walks Content.status through every state in
section 7: UPLOADED -> PROCESSING -> TRANSCRIBING -> UNDERSTANDING ->
GENERATING -> COMPLETED (or FAILED with a message at whichever step broke).
"""
import logging
import os
import uuid

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.media.ffmpeg_utils import extract_audio, get_media_duration_seconds
from app.media.text_extractor import extract_pdf_pages, extract_pptx_slides
from app.media.whisper_transcriber import transcribe_audio
from app.models.content import Content, ContentChunk, ContentType, ProcessingStatus
from app.rag.chunker import chunk_pages, chunk_transcript
from app.rag.embeddings import embed_texts
from app.rag.vector_store import add_chunks, delete_content_chunks
from app.services.summary_service import generate_summary_and_concepts

logger = logging.getLogger("vivaforge.processing")


def process_content(content_id: uuid.UUID) -> None:
    """
    Entry point invoked via FastAPI BackgroundTasks. Opens its own DB
    session since it runs outside the request's dependency-injected one.
    """
    db: Session = SessionLocal()
    try:
        content = db.query(Content).filter(Content.id == content_id).first()
        if content is None:
            logger.error("process_content called with unknown content_id=%s", content_id)
            return

        _set_status(db, content, ProcessingStatus.PROCESSING)

        if content.content_type in (ContentType.VIDEO, ContentType.AUDIO):
            chunks = _process_media(db, content)
        else:
            chunks = _process_document(db, content)

        _set_status(db, content, ProcessingStatus.UNDERSTANDING)
        _embed_and_store_chunks(content, chunks)

        _set_status(db, content, ProcessingStatus.GENERATING)
        generate_summary_and_concepts(db, content.id)

        _set_status(db, content, ProcessingStatus.COMPLETED)

    except Exception as e:
        logger.exception("Processing failed for content_id=%s", content_id)
        db.rollback()
        content = db.query(Content).filter(Content.id == content_id).first()
        if content is not None:
            _set_status(db, content, ProcessingStatus.FAILED, message=str(e)[:500])
    finally:
        db.close()


def _set_status(db: Session, content: Content, status: ProcessingStatus, message: str | None = None) -> None:
    content.status = status
    content.status_message = message
    db.commit()


def _process_media(db: Session, content: Content) -> list[ContentChunk]:
    content.duration_seconds = get_media_duration_seconds(content.storage_path)
    db.commit()

    if content.content_type == ContentType.VIDEO:
        audio_path = content.storage_path + ".extracted.wav"
        extract_audio(content.storage_path, audio_path)
    else:
        audio_path = content.storage_path  # already audio

    _set_status(db, content, ProcessingStatus.TRANSCRIBING)
    segments = transcribe_audio(audio_path)
    if content.content_type == ContentType.VIDEO and os.path.exists(audio_path) and audio_path != content.storage_path:
        os.remove(audio_path)  # don't keep the extracted intermediate file around

    chunk_data_list = chunk_transcript(segments)
    return _persist_chunks(db, content, chunk_data_list)


def _process_document(db: Session, content: Content) -> list[ContentChunk]:
    if content.content_type == ContentType.PDF:
        pages = extract_pdf_pages(content.storage_path)
    else:
        pages = extract_pptx_slides(content.storage_path)

    content.page_count = len(pages)
    db.commit()

    chunk_data_list = chunk_pages(pages)
    return _persist_chunks(db, content, chunk_data_list)


def _persist_chunks(db: Session, content: Content, chunk_data_list) -> list[ContentChunk]:
    delete_content_chunks(str(content.id))  # clear any stale vectors if this is a reprocess
    db.query(ContentChunk).filter(ContentChunk.content_id == content.id).delete()
    db.commit()

    rows = []
    for i, cd in enumerate(chunk_data_list):
        row = ContentChunk(
            content_id=content.id,
            chunk_index=i,
            text=cd.text,
            start_time_seconds=cd.start_time_seconds,
            end_time_seconds=cd.end_time_seconds,
            page_number=cd.page_number,
        )
        db.add(row)
        rows.append(row)
    db.commit()
    for row in rows:
        db.refresh(row)
    return rows


def _embed_and_store_chunks(content: Content, chunks: list[ContentChunk]) -> None:
    if not chunks:
        raise RuntimeError("No chunks were produced from this content — nothing to embed.")
    texts = [c.text for c in chunks]
    vectors = embed_texts(texts)
    add_chunks(
        content_id=str(content.id),
        chunk_ids=[str(c.id) for c in chunks],
        texts=texts,
        embeddings=vectors,
    )
