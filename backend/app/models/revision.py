import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Integer, JSON, func, DateTime, Boolean
from app.utils.db_types import GUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RevisionPlan(Base):
    """
    A generated 'today's revision' plan for a user, derived from ConceptMastery scores.

    `items_json` is an ordered list of {concept_id, concept_name, mastery_score,
    estimated_minutes} — regenerated whenever mastery scores change meaningfully
    (not on every dashboard load — see knowledge_gap_service caching notes).
    """

    __tablename__ = "revision_plans"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id"), nullable=False)

    items_json: Mapped[list] = mapped_column(JSON, nullable=False)
    estimated_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
