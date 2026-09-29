import json
import os
import uuid

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.ai.llm_client import call_llm_json
from app.ai.prompts.flashcard_prompts import FLASHCARD_SYSTEM_PROMPT, build_flashcard_prompt
from app.config import get_settings
from app.models.artifact import Artifact, ArtifactType
from app.models.concept import Concept
from app.rag.retriever import retrieve_all_chunks_ordered
from app.schemas.ai_outputs import FlashcardSetLLMOutput
from app.services.mastery_service import update_mastery
from app.services.summary_service import MAX_CONTEXT_CHARS

settings = get_settings()


def _cache_path(content_id: uuid.UUID) -> str:
    return os.path.join(settings.ARTIFACT_DIR, f"{content_id}_flashcards.json")


def get_or_generate_flashcards(db: Session, content_id: uuid.UUID) -> list[dict]:
    path = _cache_path(content_id)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)

    chunks = retrieve_all_chunks_ordered(db, content_id)
    if not chunks:
        raise RuntimeError("No content available to generate flashcards from.")

    context, total = [], 0
    for c in chunks:
        piece = f"[{c.source_label()}]\n{c.text}"
        if total + len(piece) > MAX_CONTEXT_CHARS:
            break
        context.append(piece)
        total += len(piece)

    raw = call_llm_json(FLASHCARD_SYSTEM_PROMPT, build_flashcard_prompt("\n\n".join(context)), max_tokens=2000)
    try:
        result = FlashcardSetLLMOutput.model_validate(raw)
    except ValidationError as e:
        raise RuntimeError(f"Flashcard generation returned an unexpected shape: {e}")

    cards = [c.model_dump() for c in result.cards]

    os.makedirs(settings.ARTIFACT_DIR, exist_ok=True)
    with open(path, "w") as f:
        json.dump(cards, f, indent=2)

    db.add(Artifact(content_id=content_id, artifact_type=ArtifactType.FLASHCARD_SET, storage_path=path))
    db.commit()

    return cards


def mark_card(db: Session, user_id: uuid.UUID, content_id: uuid.UUID, concept_name: str, status: str) -> None:
    """status: 'mastered' or 'difficult' — feeds straight into the same mastery score
    the viva/Explain-It-Back use, so it influences revision recommendations too."""
    concept = (
        db.query(Concept)
        .filter(Concept.content_id == content_id, Concept.name.ilike(f"%{concept_name}%"))
        .first()
    )
    if concept is None:
        return
    score = 90.0 if status == "mastered" else 30.0
    update_mastery(db, user_id, concept.id, score)
