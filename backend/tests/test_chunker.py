from app.media.text_extractor import PageText
from app.media.whisper_transcriber import TranscriptSegment
from app.rag.chunker import chunk_pages, chunk_transcript


def test_chunk_transcript_groups_segments_until_max_chars():
    segments = [TranscriptSegment(start=i * 2.0, end=i * 2.0 + 2.0, text="word " * 30) for i in range(10)]
    chunks = chunk_transcript(segments)

    assert len(chunks) > 1
    for c in chunks:
        assert c.start_time_seconds is not None
        assert c.end_time_seconds is not None
        assert c.page_number is None


def test_chunk_transcript_preserves_first_and_last_timestamp():
    segments = [
        TranscriptSegment(start=0.0, end=2.0, text="Hello there."),
        TranscriptSegment(start=2.0, end=4.5, text="This is a short segment."),
    ]
    chunks = chunk_transcript(segments)
    assert len(chunks) == 1
    assert chunks[0].start_time_seconds == 0.0
    assert chunks[0].end_time_seconds == 4.5


def test_chunk_transcript_empty_input():
    assert chunk_transcript([]) == []


def test_chunk_pages_one_chunk_per_short_page():
    pages = [PageText(page_number=1, text="Short page one."), PageText(page_number=2, text="Short page two.")]
    chunks = chunk_pages(pages)
    assert len(chunks) == 2
    assert chunks[0].page_number == 1
    assert chunks[1].page_number == 2
    for c in chunks:
        assert c.start_time_seconds is None


def test_chunk_pages_splits_unusually_long_page():
    long_text = "\n\n".join(["This is a paragraph with some content. " * 10 for _ in range(10)])
    pages = [PageText(page_number=1, text=long_text)]
    chunks = chunk_pages(pages)

    assert len(chunks) > 1
    assert all(c.page_number == 1 for c in chunks)
