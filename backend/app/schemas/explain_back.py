import uuid

from pydantic import BaseModel


class ExplainBackPromptRead(BaseModel):
    concept_id: uuid.UUID
    concept_name: str
    prompt_text: str  # e.g. "Explain Normalization in 60 seconds."


class ExplainBackSubmitRequest(BaseModel):
    content_id: uuid.UUID
    concept_id: uuid.UUID
    explanation_text: str


class ExplainBackResultRead(BaseModel):
    covered_points: list[str]
    missing_points: list[str]
    incorrect_points: list[str]
    mastery_percent: float
    recommendation: str
