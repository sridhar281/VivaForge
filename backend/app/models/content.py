import enum
import uuid
from datetime import datetime

from sqlalchemy import Enum, Float, ForeignKey, Integer, String, Text, func, DateTime
from app.utils.db_types import GUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ContentType(str, enum.Enum):
    VIDEO = "video"
    AUDIO = "audio"
    PDF = "pdf"
    PPTX = "pptx"


class ProcessingStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    TRANSCRIBING = "transcribing"
    UNDERSTANDING = "understanding"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class Content(Base):
    """A single piece of uploaded source material (video/audio/pdf/pptx)."""

    __tablename__ = "contents"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id"), nullable=False)

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content_type: Mapped[ContentType] = mapped_column(
        Enum(ContentType, values_callable=lambda obj: [e.value for e in obj]), nullable=False
    )
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)

    status: Mapped[ProcessingStatus] = mapped_column(
        Enum(ProcessingStatus, values_callable=lambda obj: [e.value for e in obj]),
        default=ProcessingStatus.UPLOADED, nullable=False
    )
    status_message: Mapped[str] = mapped_column(Text, nullable=True)  # e.g. failure reason

    duration_seconds: Mapped[float] = mapped_column(Float, nullable=True)  # for video/audio
    page_count: Mapped[int] = mapped_column(Integer, nullable=True)  # for pdf/pptx

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    owner: Mapped["User"] = relationship(back_populates="contents")
    chunks: Mapped[list["ContentChunk"]] = relationship(back_populates="content", cascade="all, delete-orphan")
    concepts: Mapped[list["Concept"]] = relationship(back_populates="content", cascade="all, delete-orphan")
    artifacts: Mapped[list["Artifact"]] = relationship(back_populates="content", cascade="all, delete-orphan")


class ContentChunk(Base):
    """
    A single retrievable unit of source text, with source-grounding metadata.

    For video/audio: start_time/end_time are populated, page_number is null.
    For PDF/PPTX: page_number is populated, start_time/end_time are null.

    The chunk's embedding itself lives in the vector store (Chroma), keyed by
    this row's id — Postgres holds the text + metadata, Chroma holds the vector.
    """

    __tablename__ = "content_chunks"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    content_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("contents.id"), nullable=False)

    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    topic_label: Mapped[str] = mapped_column(String(255), nullable=True)

    start_time_seconds: Mapped[float] = mapped_column(Float, nullable=True)
    end_time_seconds: Mapped[float] = mapped_column(Float, nullable=True)
    page_number: Mapped[int] = mapped_column(Integer, nullable=True)

    embedded: Mapped[bool] = mapped_column(default=False)  # whether vector exists in Chroma yet

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    content: Mapped["Content"] = relationship(back_populates="chunks")

    def source_label(self) -> str:
        """Human-readable citation, e.g. '02:14 - 03:01' or 'Page 7'."""
        if self.page_number is not None:
            return f"Page {self.page_number}"
        if self.start_time_seconds is not None and self.end_time_seconds is not None:
            def fmt(s: float) -> str:
                m, s = divmod(int(s), 60)
                return f"{m:02d}:{s:02d}"
            return f"{fmt(self.start_time_seconds)} - {fmt(self.end_time_seconds)}"
        return "Unknown source"
