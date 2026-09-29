import enum
import uuid
from datetime import datetime

from sqlalchemy import Enum, Float, ForeignKey, Integer, String, Text, JSON, func, DateTime
from app.utils.db_types import GUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DifficultyLevel(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class VivaSessionStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"


class VivaSession(Base):
    """One live AI-viva conversation for a given user + content."""

    __tablename__ = "viva_sessions"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id"), nullable=False)
    content_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("contents.id"), nullable=False)

    status: Mapped[VivaSessionStatus] = mapped_column(
        Enum(VivaSessionStatus, values_callable=lambda obj: [e.value for e in obj]),
        default=VivaSessionStatus.ACTIVE,
    )
    current_difficulty: Mapped[DifficultyLevel] = mapped_column(
        Enum(DifficultyLevel, values_callable=lambda obj: [e.value for e in obj]),
        default=DifficultyLevel.EASY,
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="viva_sessions")
    content: Mapped["Content"] = relationship()
    questions: Mapped[list["VivaQuestion"]] = relationship(back_populates="session", cascade="all, delete-orphan")


class VivaQuestion(Base):
    __tablename__ = "viva_questions"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("viva_sessions.id"), nullable=False)
    concept_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("concepts.id"), nullable=True)

    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[DifficultyLevel] = mapped_column(
        Enum(DifficultyLevel, values_callable=lambda obj: [e.value for e in obj]), nullable=False
    )
    source_chunk_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("content_chunks.id"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    session: Mapped["VivaSession"] = relationship(back_populates="questions")
    answer: Mapped["VivaAnswer"] = relationship(back_populates="question", uselist=False, cascade="all, delete-orphan")
    source_chunk: Mapped["ContentChunk"] = relationship()


class VivaAnswer(Base):
    """
    A user's answer plus the structured LLM evaluation of it.

    `evaluation_json` stores the raw validated evaluator output (score,
    correct/missing/incorrect concepts, feedback) so the full evaluation is
    auditable, while the individual columns below are denormalized for fast
    dashboard queries.
    """

    __tablename__ = "viva_answers"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    question_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("viva_questions.id"), nullable=False)

    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    was_spoken: Mapped[bool] = mapped_column(default=False)  # true if submitted via speech-to-text

    score: Mapped[float] = mapped_column(Float, nullable=True)  # 0-10
    correctness: Mapped[float] = mapped_column(Float, nullable=True)
    completeness: Mapped[float] = mapped_column(Float, nullable=True)
    relevance: Mapped[float] = mapped_column(Float, nullable=True)
    feedback: Mapped[str] = mapped_column(Text, nullable=True)
    evaluation_json: Mapped[dict] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    question: Mapped["VivaQuestion"] = relationship(back_populates="answer")
