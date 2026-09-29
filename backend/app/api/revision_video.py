import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.services import content_service, revision_video_service

router = APIRouter(prefix="/content", tags=["revision-video"])


class RevisionSceneRead(BaseModel):
    concept: str
    narration: str
    subtitle_text: str
    source_label: str | None


@router.get("/{content_id}/revision-video", response_model=list[RevisionSceneRead])
def get_revision_video(content_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Returns a narrated storyboard (see revision_video_service docstring for why
    this isn't an actual rendered .mp4). The frontend renders it as a
    scene-by-scene revision reel.
    """
    content = content_service.get_content_or_none(db, content_id, current_user.id)
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found.")
    try:
        return revision_video_service.get_or_generate_revision_script(db, content_id)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
