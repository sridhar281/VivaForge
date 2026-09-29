import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.artifact import Artifact
from app.models.content import Content
from app.models.user import User
from app.schemas.viva import (
    AnswerSubmitRequest,
    AnswerSubmitResponse,
    EvaluationRead,
    QuestionRead,
    SessionStartResponse,
)
from app.services import content_service, viva_session_service
from app.services.viva_pdf_service import generate_viva_pdf_for_content

router = APIRouter(tags=["viva"])


def _question_to_read(question) -> QuestionRead:
    return QuestionRead(
        id=question.id,
        question_text=question.question_text,
        difficulty=question.difficulty,
        sequence_number=question.sequence_number,
        source_label=question.source_chunk.source_label() if question.source_chunk else None,
    )


@router.post("/content/{content_id}/viva/generate", status_code=201)
def generate_viva_pdf_route(
    content_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    content = content_service.get_content_or_none(db, content_id, current_user.id)
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found.")
    try:
        artifact = generate_viva_pdf_for_content(db, content_id)
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"artifact_id": artifact.id}


@router.get("/artifacts/{artifact_id}")
def download_artifact(artifact_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    artifact = db.query(Artifact).join(Content).filter(Artifact.id == artifact_id, Content.owner_id == current_user.id).first()
    if artifact is None:
        raise HTTPException(status_code=404, detail="Artifact not found.")
    return FileResponse(artifact.storage_path)


@router.post("/viva/session", response_model=SessionStartResponse, status_code=201)
def start_viva_session(content_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    content = content_service.get_content_or_none(db, content_id, current_user.id)
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found.")
    try:
        session, question = viva_session_service.start_session(db, current_user.id, content_id)
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    return SessionStartResponse(session_id=session.id, status=session.status, first_question=_question_to_read(question))


@router.post("/viva/session/{session_id}/answer", response_model=AnswerSubmitResponse)
def submit_answer(
    session_id: uuid.UUID,
    payload: AnswerSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        answer, next_question, completed = viva_session_service.submit_answer(
            db, current_user.id, session_id, payload.question_id, payload.answer_text, payload.was_spoken
        )
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    return AnswerSubmitResponse(
        evaluation=EvaluationRead(**answer.evaluation_json),
        session_completed=completed,
        next_question=_question_to_read(next_question) if next_question else None,
    )
