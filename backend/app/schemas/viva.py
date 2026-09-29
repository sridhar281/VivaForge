import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.viva import DifficultyLevel, VivaSessionStatus


class QuestionRead(BaseModel):
    id: uuid.UUID
    question_text: str
    difficulty: DifficultyLevel
    sequence_number: int
    source_label: str | None

    class Config:
        from_attributes = True


class SessionStartResponse(BaseModel):
    session_id: uuid.UUID
    status: VivaSessionStatus
    first_question: QuestionRead


class AnswerSubmitRequest(BaseModel):
    question_id: uuid.UUID
    answer_text: str
    was_spoken: bool = False


class EvaluationRead(BaseModel):
    score: float
    correctness: float
    completeness: float
    relevance: float
    correct_concepts: list[str]
    missing_concepts: list[str]
    incorrect_claims: list[str]
    unsupported_claims: list[str]
    feedback: str


class AnswerSubmitResponse(BaseModel):
    evaluation: EvaluationRead
    session_completed: bool
    next_question: QuestionRead | None


class VivaSessionRead(BaseModel):
    id: uuid.UUID
    content_id: uuid.UUID
    status: VivaSessionStatus
    current_difficulty: DifficultyLevel
    created_at: datetime

    class Config:
        from_attributes = True
