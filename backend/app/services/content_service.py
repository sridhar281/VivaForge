import os
import uuid

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.content import Content, ContentType, ProcessingStatus

settings = get_settings()

_EXTENSION_TO_TYPE = {
    "mp4": ContentType.VIDEO,
    "mp3": ContentType.AUDIO,
    "wav": ContentType.AUDIO,
    "pdf": ContentType.PDF,
    "ppt": ContentType.PPTX,
    "pptx": ContentType.PPTX,
}


class UploadValidationError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def _safe_filename(original_filename: str) -> str:
    """Strip path components and force a random prefix so filenames can never collide or traverse directories."""
    base = os.path.basename(original_filename)
    ext = base.rsplit(".", 1)[-1].lower() if "." in base else ""
    return f"{uuid.uuid4().hex}.{ext}"


def validate_upload(file: UploadFile, file_size_bytes: int) -> ContentType:
    if not file.filename or "." not in file.filename:
        raise UploadValidationError("File must have a valid extension.")

    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in settings.allowed_extensions_set:
        raise UploadValidationError(
            f"Unsupported file type '.{ext}'. Allowed: {', '.join(sorted(settings.allowed_extensions_set))}."
        )

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size_bytes > max_bytes:
        raise UploadValidationError(f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB}MB upload limit.")
    if file_size_bytes == 0:
        raise UploadValidationError("Uploaded file is empty.")

    return _EXTENSION_TO_TYPE[ext]


def save_upload_to_disk(file: UploadFile, raw_bytes: bytes) -> str:
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    safe_name = _safe_filename(file.filename)
    dest_path = os.path.join(settings.UPLOAD_DIR, safe_name)
    with open(dest_path, "wb") as f:
        f.write(raw_bytes)
    return dest_path


def create_content_record(
    db: Session,
    owner_id: uuid.UUID,
    title: str,
    content_type: ContentType,
    original_filename: str,
    storage_path: str,
    file_size_bytes: int,
) -> Content:
    content = Content(
        owner_id=owner_id,
        title=title,
        content_type=content_type,
        original_filename=original_filename,
        storage_path=storage_path,
        file_size_bytes=file_size_bytes,
        status=ProcessingStatus.UPLOADED,
    )
    db.add(content)
    db.commit()
    db.refresh(content)
    return content


def list_user_content(db: Session, owner_id: uuid.UUID) -> list[Content]:
    return db.query(Content).filter(Content.owner_id == owner_id).order_by(Content.created_at.desc()).all()


def get_content_or_none(db: Session, content_id: uuid.UUID, owner_id: uuid.UUID) -> Content | None:
    return db.query(Content).filter(Content.id == content_id, Content.owner_id == owner_id).first()


def update_status(db: Session, content: Content, status: ProcessingStatus, message: str | None = None) -> None:
    content.status = status
    content.status_message = message
    db.commit()
