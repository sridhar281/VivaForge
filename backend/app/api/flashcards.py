import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.services import content_service, flashcard_service

router = APIRouter(prefix="/content", tags=["flashcards"])


class FlashcardRead(BaseModel):
    front: str
    back: str
    concept: str


class MarkCardRequest(BaseModel):
    concept: str
    status: str  # "mastered" | "difficult"


@router.get("/{content_id}/flashcards", response_model=list[FlashcardRead])
def get_flashcards(content_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    content = content_service.get_content_or_none(db, content_id, current_user.id)
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found.")
    try:
        return flashcard_service.get_or_generate_flashcards(db, content_id)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{content_id}/flashcards/mark", status_code=204)
def mark_flashcard(
    content_id: uuid.UUID,
    payload: MarkCardRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    content = content_service.get_content_or_none(db, content_id, current_user.id)
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found.")
    flashcard_service.mark_card(db, current_user.id, content_id, payload.concept, payload.status)
