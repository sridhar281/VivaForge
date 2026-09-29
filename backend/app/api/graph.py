import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.services import content_service
from app.services.graph_service import GraphRead, build_graph

router = APIRouter(prefix="/content", tags=["graph"])


@router.get("/{content_id}/graph", response_model=GraphRead)
def get_graph(content_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    content = content_service.get_content_or_none(db, content_id, current_user.id)
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found.")
    return build_graph(db, current_user.id, content_id)
