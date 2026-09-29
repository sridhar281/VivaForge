import json
import os
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.config import get_settings
from app.database import get_db
from app.models.concept import Concept
from app.models.content import Content
from app.models.user import User
from app.schemas.content import ConceptRead, ContentRead, ContentStatusRead, SummaryRead
from app.services import content_service
from app.services.processing_service import process_content

router = APIRouter(prefix="/content", tags=["content"])
settings = get_settings()


@router.post("/upload", response_model=ContentRead, status_code=201)
async def upload_content(
    file: UploadFile,
    title: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    raw_bytes = await file.read()
    try:
        content_type = content_service.validate_upload(file, len(raw_bytes))
    except content_service.UploadValidationError as e:
        raise HTTPException(status_code=422, detail=e.message)

    storage_path = content_service.save_upload_to_disk(file, raw_bytes)
    content = content_service.create_content_record(
        db,
        owner_id=current_user.id,
        title=title or file.filename,
        content_type=content_type,
        original_filename=file.filename,
        storage_path=storage_path,
        file_size_bytes=len(raw_bytes),
    )
    return content


@router.get("", response_model=list[ContentRead])
def list_content(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return content_service.list_user_content(db, current_user.id)


@router.get("/{content_id}", response_model=ContentRead)
def get_content(content_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    content = content_service.get_content_or_none(db, content_id, current_user.id)
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found.")
    return content


@router.post("/{content_id}/process", status_code=202)
def trigger_processing(
    content_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    content = content_service.get_content_or_none(db, content_id, current_user.id)
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found.")

    background_tasks.add_task(process_content, content.id)
    return {"detail": "Processing started."}


@router.get("/{content_id}/status", response_model=ContentStatusRead)
def get_status(content_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    content = content_service.get_content_or_none(db, content_id, current_user.id)
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found.")
    return content


@router.get("/{content_id}/summary", response_model=SummaryRead)
def get_summary(content_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    content = content_service.get_content_or_none(db, content_id, current_user.id)
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found.")

    summary_path = os.path.join(settings.ARTIFACT_DIR, f"{content_id}_summary.json")
    if not os.path.exists(summary_path):
        raise HTTPException(status_code=404, detail="Summary not generated yet — has processing completed?")
    with open(summary_path) as f:
        return json.load(f)


@router.get("/{content_id}/concepts", response_model=list[ConceptRead])
def get_concepts(content_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    content = content_service.get_content_or_none(db, content_id, current_user.id)
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found.")

    concepts = db.query(Concept).filter(Concept.content_id == content_id).all()
    return [
        ConceptRead(
            id=c.id,
            name=c.name,
            explanation=c.explanation,
            source_label=c.source_chunk.source_label() if c.source_chunk else None,
        )
        for c in concepts
    ]
