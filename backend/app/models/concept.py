import enum
import uuid
from datetime import datetime

from sqlalchemy import Enum, Float, ForeignKey, String, Text, UniqueConstraint, func, DateTime
from app.utils.db_types import GUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RelationType(str, enum.Enum):
    PREREQUISITE = "prerequisite"
    RELATED_TO = "related_to"
    PART_OF = "part_of"
    EXAMPLE_OF = "example_of"
    DEPENDS_ON = "depends_on"


class Concept(Base):
    """A single extracted concept/node in the knowledge graph, scoped to one Content item."""

    __tablename__ = "concepts"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    content_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("contents.id"), nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=True)
    # Best supporting chunk for "view source" — nullable because extraction may not always
    # find a single clean anchor chunk.
    source_chunk_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("content_chunks.id"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    content: Mapped["Content"] = relationship(back_populates="concepts")
    source_chunk: Mapped["ContentChunk"] = relationship()
    mastery_records: Mapped[list["ConceptMastery"]] = relationship(
        back_populates="concept", cascade="all, delete-orphan"
    )


class ConceptEdge(Base):
    """A directed relationship between two concepts, e.g. Normalization --prerequisite--> 2NF."""

    __tablename__ = "concept_edges"
    __table_args__ = (UniqueConstraint("source_concept_id", "target_concept_id", "relation_type"),)

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    source_concept_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("concepts.id"), nullable=False)
    target_concept_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("concepts.id"), nullable=False)
    relation_type: Mapped[RelationType] = mapped_column(
        Enum(RelationType, values_callable=lambda obj: [e.value for e in obj]), nullable=False
    )


class ConceptMastery(Base):
    """
    Per-user, per-concept running mastery score (0-100).

    This is the row the Knowledge Gap Engine and dashboard read from — updated
    after every viva answer / Explain-It-Back attempt that touches this concept.
    """

    __tablename__ = "concept_mastery"
    __table_args__ = (UniqueConstraint("user_id", "concept_id"),)

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id"), nullable=False)
    concept_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("concepts.id"), nullable=False)

    mastery_score: Mapped[float] = mapped_column(Float, default=0.0)  # 0-100
    attempts: Mapped[int] = mapped_column(default=0)
    last_evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    concept: Mapped["Concept"] = relationship(back_populates="mastery_records")
