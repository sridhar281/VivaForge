"""
Chunking strategy — deliberately simple:
- Video/audio: group consecutive Whisper segments until ~MAX_CHARS is reached.
  Each chunk keeps the start time of its first segment and end time of its last.
- PDF/PPTX: one chunk per page/slide; if a page is unusually long, split it
  into paragraph-sized pieces (still tagged with the same page number).
"""
from dataclasses import dataclass

from app.media.text_extractor import PageText
from app.media.whisper_transcriber import TranscriptSegment

MAX_CHUNK_CHARS = 900


@dataclass
class ChunkData:
    text: str
    start_time_seconds: float | None = None
    end_time_seconds: float | None = None
    page_number: int | None = None


def chunk_transcript(segments: list[TranscriptSegment]) -> list[ChunkData]:
    chunks: list[ChunkData] = []
    buffer_text: list[str] = []
    buffer_start: float | None = None
    buffer_end: float | None = None

    def flush():
        if buffer_text:
            chunks.append(
                ChunkData(
                    text=" ".join(buffer_text).strip(),
                    start_time_seconds=buffer_start,
                    end_time_seconds=buffer_end,
                )
            )

    for seg in segments:
        if buffer_start is None:
            buffer_start = seg.start
        buffer_text.append(seg.text)
        buffer_end = seg.end

        if sum(len(t) for t in buffer_text) >= MAX_CHUNK_CHARS:
            flush()
            buffer_text, buffer_start, buffer_end = [], None, None

    flush()
    return chunks


def chunk_pages(pages: list[PageText]) -> list[ChunkData]:
    chunks: list[ChunkData] = []
    for page in pages:
        if len(page.text) <= MAX_CHUNK_CHARS:
            chunks.append(ChunkData(text=page.text, page_number=page.page_number))
            continue

        # Split an unusually long page into paragraph-sized pieces, same page number.
        paragraphs = [p.strip() for p in page.text.split("\n\n") if p.strip()]
        buffer = ""
        for para in paragraphs:
            if buffer and len(buffer) + len(para) > MAX_CHUNK_CHARS:
                chunks.append(ChunkData(text=buffer.strip(), page_number=page.page_number))
                buffer = ""
            buffer += para + "\n\n"
        if buffer.strip():
            chunks.append(ChunkData(text=buffer.strip(), page_number=page.page_number))
    return chunks
