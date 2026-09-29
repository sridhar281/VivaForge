"""
Speech-to-text via faster-whisper (CPU-friendly, same accuracy as OpenAI's
original Whisper implementation). The model is loaded once and reused.

The faster_whisper import is deliberately deferred to inside _get_model()
rather than done at module load time. This file is imported by the main
app startup chain (main.py -> api/content.py -> services/processing_service.py
-> here), so an import-time failure here would crash the ENTIRE backend --
including features (auth, PDF upload, viva) that have nothing to do with
video transcription. A lazy import means a faster-whisper install problem
only surfaces when someone actually tries to transcribe video/audio, with
a clear error, instead of taking down every endpoint in the app.
"""
from dataclasses import dataclass
from functools import lru_cache

from app.config import get_settings

settings = get_settings()


@dataclass
class TranscriptSegment:
    start: float
    end: float
    text: str


@lru_cache
def _get_model():
    try:
        from faster_whisper import WhisperModel
    except ImportError as e:
        raise RuntimeError(
            "faster-whisper is not installed correctly, so video/audio transcription "
            "isn't available right now. Other features (PDF/PPTX upload, auth, viva on "
            "already-processed content) are unaffected. "
            f"Original error: {e}"
        )
    return WhisperModel(settings.WHISPER_MODEL_SIZE, device=settings.WHISPER_DEVICE, compute_type="int8")


def transcribe_audio(audio_path: str) -> list[TranscriptSegment]:
    """
    Transcribe a WAV file into timestamped segments. Raises RuntimeError on failure
    so the caller can mark Content.status = FAILED with a useful message.
    """
    try:
        model = _get_model()
        segments, _info = model.transcribe(audio_path, beam_size=5)
        return [TranscriptSegment(start=s.start, end=s.end, text=s.text.strip()) for s in segments if s.text.strip()]
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"Transcription failed: {e}")
