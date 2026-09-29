import json
import os
import uuid

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.ai.llm_client import call_llm_json
from app.ai.prompts.question_prompts import QUESTION_CHAIN_SYSTEM_PROMPT, build_question_chain_prompt
from app.config import get_settings
from app.models.artifact import Artifact, ArtifactType
from app.models.concept import Concept
from app.models.content import Content
from app.pdf.viva_pdf_generator import generate_viva_pdf
from app.rag.retriever import retrieve_context
from app.schemas.ai_outputs import QuestionChainLLMOutput

settings = get_settings()


def generate_viva_pdf_for_content(db: Session, content_id: uuid.UUID) -> Artifact:
    content = db.query(Content).filter(Content.id == content_id).first()
    if content is None:
        raise ValueError("Content not found.")

    concepts = db.query(Concept).filter(Concept.content_id == content_id).all()
    if not concepts:
        raise RuntimeError("No concepts have been extracted for this content yet — has processing completed?")

    summary_path = os.path.join(settings.ARTIFACT_DIR, f"{content_id}_summary.json")
    if not os.path.exists(summary_path):
        raise RuntimeError("Summary artifact not found — has processing completed?")
    with open(summary_path) as f:
        summary = json.load(f)

    question_chains = []
    for concept in concepts:
        retrieval = retrieve_context(db, content_id, query=concept.name, top_k=4)
        source_text = retrieval.context_text or (concept.explanation or concept.name)

        raw = call_llm_json(
            QUESTION_CHAIN_SYSTEM_PROMPT, build_question_chain_prompt(concept.name, source_text), max_tokens=1200
        )
        try:
            chain = QuestionChainLLMOutput.model_validate(raw)
        except ValidationError:
            continue  # skip a malformed chain rather than failing the whole PDF

        question_chains.append({"concept": concept.name, **chain.model_dump()})

    if not question_chains:
        raise RuntimeError("Question generation failed for every concept — could not build the PDF.")

    os.makedirs(settings.ARTIFACT_DIR, exist_ok=True)
    pdf_path = os.path.join(settings.ARTIFACT_DIR, f"{content_id}_viva.pdf")
    generate_viva_pdf(
        output_path=pdf_path,
        content_title=content.title,
        executive_summary=summary["executive_summary"],
        key_concepts=summary["key_concepts"],
        definitions=summary["definitions"],
        question_chains=question_chains,
    )

    artifact = Artifact(content_id=content_id, artifact_type=ArtifactType.VIVA_PDF, storage_path=pdf_path)
    db.add(artifact)
    db.commit()
    db.refresh(artifact)
    return artifact
