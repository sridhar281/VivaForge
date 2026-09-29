import uuid

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.ai.llm_client import call_llm_json
from app.ai.prompts.explain_back_prompts import EXPLAIN_BACK_SYSTEM_PROMPT, build_explain_back_prompt
from app.models.concept import Concept, ConceptMastery
from app.rag.retriever import retrieve_context
from app.schemas.ai_outputs import ExplainBackLLMOutput
from app.services.mastery_service import update_mastery


def pick_concept_to_explain(db: Session, user_id: uuid.UUID, content_id: uuid.UUID) -> Concept:
    """
    Prefer the user's weakest concept for this content (the whole point of
    Explain-It-Back is targeting gaps); fall back to any concept if the
    user has no mastery history yet.
    """
    concepts = db.query(Concept).filter(Concept.content_id == content_id).all()
    if not concepts:
        raise RuntimeError("No concepts available for this content yet.")

    mastery_by_concept = {
        m.concept_id: m.mastery_score
        for m in db.query(ConceptMastery).filter(
            ConceptMastery.user_id == user_id, ConceptMastery.concept_id.in_([c.id for c in concepts])
        )
    }
    # Concepts never attempted are treated as lowest priority score (0) so they surface first.
    return min(concepts, key=lambda c: mastery_by_concept.get(c.id, 0))


def evaluate_explanation(
    db: Session, user_id: uuid.UUID, content_id: uuid.UUID, concept_id: uuid.UUID, user_explanation: str
) -> ExplainBackLLMOutput:
    concept = db.query(Concept).filter(Concept.id == concept_id, Concept.content_id == content_id).first()
    if concept is None:
        raise ValueError("Concept not found for this content.")

    retrieval = retrieve_context(db, content_id, query=concept.name, top_k=4)
    source_text = retrieval.context_text or (concept.explanation or concept.name)

    raw = call_llm_json(
        EXPLAIN_BACK_SYSTEM_PROMPT,
        build_explain_back_prompt(concept.name, source_text, user_explanation),
        max_tokens=800,
    )
    try:
        result = ExplainBackLLMOutput.model_validate(raw)
    except ValidationError as e:
        raise RuntimeError(f"Explain-It-Back evaluation returned an unexpected shape: {e}")

    update_mastery(db, user_id, concept_id, result.mastery_percent)
    return result
