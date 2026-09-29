"""
One reusable retrieval function, used by every feature that needs
source-grounded context (summary generation, question generation, viva
answer evaluation, Explain-It-Back). Nothing else in the app should query
Chroma directly — this is the single seam, so swapping the vector store
later means changing one file (section 9: "don't duplicate RAG code").
"""
import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.content import ContentChunk
from app.rag.embeddings import embed_query
from app.rag.vector_store import query_similar_chunk_ids


@dataclass
class RetrievedChunk:
    chunk: ContentChunk
    source_label: str


@dataclass
class RetrievalResult:
    chunks: list[RetrievedChunk]
    context_text: str  # ready to drop into an LLM prompt, with source labels inline


def retrieve_context(db: Session, content_id: uuid.UUID, query: str, top_k: int = 5) -> RetrievalResult:
    query_embedding = embed_query(query)
    similar_ids = query_similar_chunk_ids(content_id=str(content_id), query_embedding=query_embedding, top_k=top_k)

    if not similar_ids:
        return RetrievalResult(chunks=[], context_text="")

    # Fetch full rows from Postgres, preserving Chroma's relevance order.
    rows = db.query(ContentChunk).filter(ContentChunk.id.in_(similar_ids)).all()
    rows_by_id = {str(r.id): r for r in rows}
    ordered = [rows_by_id[cid] for cid in similar_ids if cid in rows_by_id]

    retrieved = [RetrievedChunk(chunk=c, source_label=c.source_label()) for c in ordered]
    context_text = "\n\n".join(f"[Source: {rc.source_label}]\n{rc.chunk.text}" for rc in retrieved)

    return RetrievalResult(chunks=retrieved, context_text=context_text)


def retrieve_all_chunks_ordered(db: Session, content_id: uuid.UUID) -> list[ContentChunk]:
    """
    Used where we need the *whole* document in order (e.g. the initial
    executive summary), not a similarity-ranked subset.
    """
    return (
        db.query(ContentChunk)
        .filter(ContentChunk.content_id == content_id)
        .order_by(ContentChunk.chunk_index)
        .all()
    )
