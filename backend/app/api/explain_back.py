import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.explain_back import ExplainBackPromptRead, ExplainBackResultRead, ExplainBackSubmitRequest
from app.services import content_service, explain_back_service

router = APIRouter(prefix="/explain-back", tags=["explain-back"])


@router.get("/{content_id}/prompt", response_model=ExplainBackPromptRead)
def get_explain_back_prompt(content_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    content = content_service.get_content_or_none(db, content_id, current_user.id)
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found.")
    try:
        concept = explain_back_service.pick_concept_to_explain(db, current_user.id, content_id)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ExplainBackPromptRead(
        concept_id=concept.id, concept_name=concept.name, prompt_text=f"Explain {concept.name} in your own words."
    )


@router.post("/evaluate", response_model=ExplainBackResultRead)
def evaluate(payload: ExplainBackSubmitRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    content = content_service.get_content_or_none(db, payload.content_id, current_user.id)
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found.")
    try:
        result = explain_back_service.evaluate_explanation(
            db, current_user.id, payload.content_id, payload.concept_id, payload.explanation_text
        )
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ExplainBackResultRead(**result.model_dump())
