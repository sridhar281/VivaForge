"""
Section 19 explicitly allows this fallback when full automatic video
generation is unreliable/expensive: "create a technically honest
implementation using extracted clips + generated narration + subtitles.
Do not fake AI-generated video." This produces exactly that — a
scene-by-scene storyboard (narration + subtitle text + the source
timestamp/page each scene is grounded in) — rendered by the frontend as
a scrollable revision reel, not an actual .mp4. No video encoding
happens; nothing here claims otherwise.
"""
import json
import os
import uuid

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.ai.llm_client import call_llm_json
from app.ai.prompts.revision_script_prompts import REVISION_SCRIPT_SYSTEM_PROMPT, build_revision_script_prompt
from app.config import get_settings
from app.models.artifact import Artifact, ArtifactType
from app.models.concept import Concept
from app.rag.retriever import retrieve_context
from app.schemas.ai_outputs import RevisionScriptLLMOutput

settings = get_settings()


def _cache_path(content_id: uuid.UUID) -> str:
    return os.path.join(settings.ARTIFACT_DIR, f"{content_id}_revision_script.json")


def get_or_generate_revision_script(db: Session, content_id: uuid.UUID) -> list[dict]:
    path = _cache_path(content_id)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)

    concepts = db.query(Concept).filter(Concept.content_id == content_id).all()
    if not concepts:
        raise RuntimeError("No concepts available to build a revision script from.")

    # Build context from the concepts themselves (a compact, already-curated source)
    # rather than the whole transcript — keeps the script focused and cheap to generate.
    concept_summaries = "\n".join(f"- {c.name}: {c.explanation or ''}" for c in concepts)

    raw = call_llm_json(
        REVISION_SCRIPT_SYSTEM_PROMPT, build_revision_script_prompt(concept_summaries), max_tokens=1200
    )
    try:
        result = RevisionScriptLLMOutput.model_validate(raw)
    except ValidationError as e:
        raise RuntimeError(f"Revision script generation returned an unexpected shape: {e}")

    scenes = []
    for scene in result.scenes:
        retrieval = retrieve_context(db, content_id, query=scene.concept, top_k=1)
        source_label = retrieval.chunks[0].source_label if retrieval.chunks else None
        scenes.append({**scene.model_dump(), "source_label": source_label})

    os.makedirs(settings.ARTIFACT_DIR, exist_ok=True)
    with open(path, "w") as f:
        json.dump(scenes, f, indent=2)

    db.add(Artifact(content_id=content_id, artifact_type=ArtifactType.REVISION_VIDEO, storage_path=path))
    db.commit()

    return scenes
