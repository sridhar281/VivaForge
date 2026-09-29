import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.services.knowledge_gap_service import generate_revision_plan, get_current_plan, get_knowledge_profile

router = APIRouter(tags=["knowledge"])


class ConceptScore(BaseModel):
    concept_id: uuid.UUID
    concept_name: str
    mastery_score: float | None


class KnowledgeProfileResponse(BaseModel):
    strong_concepts: list[ConceptScore]
    weak_concepts: list[ConceptScore]
    unseen_concepts: list[ConceptScore]


class RevisionPlanItem(BaseModel):
    concept_id: str
    concept_name: str
    mastery_score: float | None
    estimated_minutes: int


class RevisionPlanResponse(BaseModel):
    id: uuid.UUID
    items: list[RevisionPlanItem]
    estimated_minutes: int
    created_at: datetime


@router.get("/knowledge-profile", response_model=KnowledgeProfileResponse)
def knowledge_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_knowledge_profile(db, current_user.id)


@router.get("/revision-plan", response_model=RevisionPlanResponse)
def revision_plan(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    plan = get_current_plan(db, current_user.id)
    if plan is None:
        plan = generate_revision_plan(db, current_user.id)
    return RevisionPlanResponse(id=plan.id, items=plan.items_json, estimated_minutes=plan.estimated_minutes, created_at=plan.created_at)


@router.post("/revision-plan/regenerate", response_model=RevisionPlanResponse)
def regenerate_revision_plan(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    plan = generate_revision_plan(db, current_user.id)
    return RevisionPlanResponse(id=plan.id, items=plan.items_json, estimated_minutes=plan.estimated_minutes, created_at=plan.created_at)
