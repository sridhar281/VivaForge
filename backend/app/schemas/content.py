import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.content import ContentType, ProcessingStatus


class ContentRead(BaseModel):
    id: uuid.UUID
    title: str
    content_type: ContentType
    original_filename: str
    status: ProcessingStatus
    status_message: str | None
    duration_seconds: float | None
    page_count: int | None
    created_at: datetime

    class Config:
        from_attributes = True


class ContentStatusRead(BaseModel):
    id: uuid.UUID
    status: ProcessingStatus
    status_message: str | None

    class Config:
        from_attributes = True


class ConceptRead(BaseModel):
    id: uuid.UUID
    name: str
    explanation: str | None
    source_label: str | None  # e.g. "02:14 - 03:01" or "Page 7"

    class Config:
        from_attributes = True


class SummaryRead(BaseModel):
    """The structured study material generated for one Content item."""
    executive_summary: str
    topic_summaries: list[dict]  # [{"topic": str, "summary": str}]
    key_concepts: list[str]
    definitions: list[dict]  # [{"term": str, "definition": str}]
    examples: list[str]
    quick_revision_notes: list[str]
