"""
Import every model here so that:
  1. `Base.metadata` knows about all tables (needed for Alembic autogenerate).
  2. SQLAlchemy relationship() string references resolve correctly.
"""
from app.models.user import User  # noqa: F401
from app.models.content import Content, ContentChunk, ContentType, ProcessingStatus  # noqa: F401
from app.models.concept import Concept, ConceptEdge, ConceptMastery, RelationType  # noqa: F401
from app.models.viva import VivaSession, VivaQuestion, VivaAnswer, DifficultyLevel, VivaSessionStatus  # noqa: F401
from app.models.artifact import Artifact, ArtifactType  # noqa: F401
from app.models.revision import RevisionPlan  # noqa: F401

__all__ = [
    "User",
    "Content",
    "ContentChunk",
    "ContentType",
    "ProcessingStatus",
    "Concept",
    "ConceptEdge",
    "ConceptMastery",
    "RelationType",
    "VivaSession",
    "VivaQuestion",
    "VivaAnswer",
    "DifficultyLevel",
    "VivaSessionStatus",
    "Artifact",
    "ArtifactType",
    "RevisionPlan",
]
