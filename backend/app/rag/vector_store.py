"""
Chroma is used purely as a vector index: chunk text + embedding + minimal
metadata (content_id, chunk_id). The chunk's full row (text, source
timestamps/page) still lives in Postgres as the source of truth — Chroma
is only used to go from "a query" to "the right chunk ids", never as the
only copy of the data. This keeps the retrieval layer swappable (section 3).
"""
import chromadb

from app.config import get_settings

settings = get_settings()

_COLLECTION_NAME = "vivaforge_chunks"

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
    return _client


def _get_collection():
    return _get_client().get_or_create_collection(_COLLECTION_NAME)


def add_chunks(content_id: str, chunk_ids: list[str], texts: list[str], embeddings: list[list[float]]) -> None:
    if not chunk_ids:
        return
    collection = _get_collection()
    collection.add(
        ids=chunk_ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=[{"content_id": content_id} for _ in chunk_ids],
    )


def query_similar_chunk_ids(content_id: str, query_embedding: list[float], top_k: int = 5) -> list[str]:
    collection = _get_collection()
    # Guard: querying an empty/nonexistent collection scope should return [], not raise.
    if collection.count() == 0:
        return []
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={"content_id": content_id},
    )
    ids = results.get("ids", [[]])
    return ids[0] if ids else []


def delete_content_chunks(content_id: str) -> None:
    """Used if a Content item is reprocessed — clears stale vectors first."""
    collection = _get_collection()
    collection.delete(where={"content_id": content_id})
