"""
Embeddings run locally via sentence-transformers (all-MiniLM-L6-v2, ~80MB,
384-dim). Chosen deliberately over a paid embeddings API: it's free, needs
no key, and is more than accurate enough for chunk retrieval at this scale.
The model downloads once on first use and is cached by the library.
"""
from functools import lru_cache

from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384


@lru_cache
def _get_model() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    model = _get_model()
    vectors = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return vectors.tolist()


def embed_query(query: str) -> list[float]:
    return embed_texts([query])[0]
