import enum
import uuid
from datetime import datetime

from sqlalchemy import Enum, ForeignKey, String, func, DateTime
from app.utils.db_types import GUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ArtifactType(str, enum.Enum):
    SUMMARY_JSON = "summary_json"
    VIVA_PDF = "viva_pdf"
    FLASHCARD_SET = "flashcard_set"
    REVISION_VIDEO = "revision_video"
    KNOWLEDGE_GRAPH_JSON = "knowledge_graph_json"


class Artifact(Base):
    """Any generated deliverable tied to a Content item (PDF, video, JSON export)."""

    __tablename__ = "artifacts"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    content_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("contents.id"), nullable=False)

    artifact_type: Mapped[ArtifactType] = mapped_column(
        Enum(ArtifactType, values_callable=lambda obj: [e.value for e in obj]), nullable=False
    )
    storage_path: Mapped[str] = mapped_column(String(1000), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    content: Mapped["Content"] = relationship(back_populates="artifacts")
