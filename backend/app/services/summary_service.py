"""
Runs once per Content item (triggered at the end of the processing
pipeline) — never regenerated on every page load (section 20: cost
control). The summary is cached to disk as an Artifact; concepts are
cached as rows in the `concepts`/`concept_edges` tables.
"""
import json
import os
import uuid

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.ai.llm_client import call_llm_json
from app.ai.prompts.concept_prompts import CONCEPT_EXTRACTION_SYSTEM_PROMPT, build_concept_extraction_prompt
from app.ai.prompts.summary_prompts import SUMMARY_SYSTEM_PROMPT, build_summary_prompt
from app.config import get_settings
from app.models.artifact import Artifact, ArtifactType
from app.models.concept import Concept, ConceptEdge, RelationType
from app.rag.retriever import retrieve_all_chunks_ordered
from app.schemas.ai_outputs import ConceptExtractionLLMOutput, SummaryLLMOutput

settings = get_settings()

MAX_CONTEXT_CHARS = 14000  # keep the summary/concept-extraction prompt within a reasonable token budget


def _build_full_context(db: Session, content_id: uuid.UUID) -> str:
    chunks = retrieve_all_chunks_ordered(db, content_id)
    if not chunks:
        raise RuntimeError("No content chunks available — processing did not produce any text.")

    parts, total_len = [], 0
    for c in chunks:
        piece = f"[{c.source_label()}]\n{c.text}"
        if total_len + len(piece) > MAX_CONTEXT_CHARS:
            break
        parts.append(piece)
        total_len += len(piece)
    return "\n\n".join(parts)


def _find_source_chunk_id(db: Session, content_id: uuid.UUID, concept_name: str) -> uuid.UUID | None:
    """Simple substring match — good enough to give 'view source' something useful most of the time."""
    from app.models.content import ContentChunk

    match = (
        db.query(ContentChunk)
        .filter(ContentChunk.content_id == content_id, ContentChunk.text.ilike(f"%{concept_name}%"))
        .first()
    )
    return match.id if match else None


def _save_summary_artifact(content_id: uuid.UUID, summary: SummaryLLMOutput) -> None:
    os.makedirs(settings.ARTIFACT_DIR, exist_ok=True)
    path = os.path.join(settings.ARTIFACT_DIR, f"{content_id}_summary.json")
    with open(path, "w") as f:
        json.dump(summary.model_dump(), f, indent=2)


def generate_summary_and_concepts(db: Session, content_id: uuid.UUID) -> None:
    context = _build_full_context(db, content_id)

    # --- Summary ---
    raw_summary = call_llm_json(SUMMARY_SYSTEM_PROMPT, build_summary_prompt(context), max_tokens=2500)
    try:
        summary = SummaryLLMOutput.model_validate(raw_summary)
    except ValidationError as e:
        raise RuntimeError(f"Summary generation returned an unexpected shape: {e}")

    _save_summary_artifact(content_id, summary)
    db.add(
        Artifact(
            content_id=content_id,
            artifact_type=ArtifactType.SUMMARY_JSON,
            storage_path=os.path.join(settings.ARTIFACT_DIR, f"{content_id}_summary.json"),
        )
    )

    # --- Concepts + relationships ---
    raw_concepts = call_llm_json(
        CONCEPT_EXTRACTION_SYSTEM_PROMPT, build_concept_extraction_prompt(context), max_tokens=2000
    )
    try:
        extraction = ConceptExtractionLLMOutput.model_validate(raw_concepts)
    except ValidationError as e:
        raise RuntimeError(f"Concept extraction returned an unexpected shape: {e}")

    name_to_id: dict[str, uuid.UUID] = {}
    for item in extraction.concepts:
        source_chunk_id = _find_source_chunk_id(db, content_id, item.name)
        concept = Concept(
            content_id=content_id,
            name=item.name,
            explanation=item.explanation,
            source_chunk_id=source_chunk_id,
        )
        db.add(concept)
        db.flush()  # get concept.id without a full commit yet
        name_to_id[item.name.strip().lower()] = concept.id

    valid_relation_types = {r.value for r in RelationType}
    for rel in extraction.relationships:
        src_id = name_to_id.get(rel.source.strip().lower())
        tgt_id = name_to_id.get(rel.target.strip().lower())
        if not src_id or not tgt_id or rel.type not in valid_relation_types:
            continue  # skip relationships the LLM invented that don't map to real concepts
        db.add(ConceptEdge(source_concept_id=src_id, target_concept_id=tgt_id, relation_type=RelationType(rel.type)))

    db.commit()
