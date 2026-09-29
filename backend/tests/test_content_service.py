import pytest

from app.services.content_service import UploadValidationError, validate_upload
from app.models.content import ContentType


class _FakeUploadFile:
    def __init__(self, filename: str):
        self.filename = filename


def test_validate_upload_accepts_supported_video():
    content_type = validate_upload(_FakeUploadFile("lecture.mp4"), file_size_bytes=1024)
    assert content_type == ContentType.VIDEO


def test_validate_upload_accepts_supported_pdf():
    content_type = validate_upload(_FakeUploadFile("notes.pdf"), file_size_bytes=1024)
    assert content_type == ContentType.PDF


def test_validate_upload_rejects_unsupported_extension():
    with pytest.raises(UploadValidationError):
        validate_upload(_FakeUploadFile("malware.exe"), file_size_bytes=1024)


def test_validate_upload_rejects_missing_extension():
    with pytest.raises(UploadValidationError):
        validate_upload(_FakeUploadFile("no_extension"), file_size_bytes=1024)


def test_validate_upload_rejects_empty_file():
    with pytest.raises(UploadValidationError):
        validate_upload(_FakeUploadFile("lecture.mp4"), file_size_bytes=0)


def test_validate_upload_rejects_oversized_file():
    from app.config import get_settings

    settings = get_settings()
    too_big = (settings.MAX_UPLOAD_SIZE_MB + 1) * 1024 * 1024
    with pytest.raises(UploadValidationError):
        validate_upload(_FakeUploadFile("lecture.mp4"), file_size_bytes=too_big)
