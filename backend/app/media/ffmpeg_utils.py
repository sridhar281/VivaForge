"""
Thin wrappers around the ffmpeg CLI (via the ffmpeg-python bindings).
Kept deliberately simple: one function per operation, no hidden state.
"""
import ffmpeg


def get_media_duration_seconds(file_path: str) -> float | None:
    """Return duration in seconds, or None if it can't be read (e.g. corrupt file)."""
    try:
        probe = ffmpeg.probe(file_path)
        return float(probe["format"]["duration"])
    except Exception:
        return None


def extract_audio(video_path: str, output_audio_path: str) -> str:
    """
    Extract mono 16kHz WAV audio from a video file — the format
    faster-whisper expects. Raises RuntimeError with ffmpeg's stderr on failure.
    """
    try:
        (
            ffmpeg.input(video_path)
            .output(output_audio_path, ac=1, ar=16000, format="wav")
            .overwrite_output()
            .run(quiet=True)
        )
    except ffmpeg.Error as e:
        stderr = e.stderr.decode(errors="ignore") if e.stderr else str(e)
        raise RuntimeError(f"FFmpeg audio extraction failed: {stderr[:500]}")
    return output_audio_path
