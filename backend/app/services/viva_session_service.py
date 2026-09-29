"""
The adaptive loop described in section 13:
  question -> answer -> evaluate -> update mastery -> pick next
  concept/difficulty -> next question.

MAX_QUESTIONS_PER_SESSION caps a session so it has a natural end (section
13 doesn't specify one, but an unbounded viva isn't a usable product).
"""
import uuid
from datetime import datetime, timezone

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.ai.llm_client import call_llm_json
from app.ai.prompts.question_prompts import SINGLE_QUESTION_SYSTEM_PROMPT, build_single_question_prompt
from app.ai.prompts.evaluation_prompts import ANSWER_EVALUATION_SYSTEM_PROMPT, build_answer_evaluation_prompt
from app.models.concept import Concept
from app.models.content import Content
from app.models.viva import DifficultyLevel, VivaAnswer, VivaQuestion, VivaSession, VivaSessionStatus
from app.rag.retriever import retrieve_context
from app.schemas.ai_outputs import AnswerEvaluationLLMOutput, SingleQuestionLLMOutput
from app.services.mastery_service import update_mastery

MAX_QUESTIONS_PER_SESSION = 8

_DIFFICULTY_ORDER = [DifficultyLevel.EASY, DifficultyLevel.MEDIUM, DifficultyLevel.HARD]


def _next_concept(db: Session, content_id: uuid.UUID, session_id: uuid.UUID, missing_concepts: list[str]) -> Concept:
    all_concepts = db.query(Concept).filter(Concept.content_id == content_id).all()
    if not all_concepts:
        raise RuntimeError("No concepts available to build a viva question from.")

    asked_concept_ids = {
        q.concept_id
        for q in db.query(VivaQuestion).filter(VivaQuestion.session_id == session_id, VivaQuestion.concept_id.isnot(None))
    }

    # Prefer a concept the last answer missed, if it exists in this content and hasn't been over-asked.
    for name in missing_concepts:
        match = next((c for c in all_concepts if name.strip().lower() in c.name.lower()), None)
        if match:
            return match

    unused = [c for c in all_concepts if c.id not in asked_concept_ids]
    if unused:
        return unused[0]
    return all_concepts[len(asked_concept_ids) % len(all_concepts)]  # cycle back if every concept has been asked


def _generate_question(
    db: Session, content: Content, session: VivaSession, concept: Concept, difficulty: DifficultyLevel
) -> str:
    retrieval = retrieve_context(db, content.id, query=concept.name, top_k=3)
    source_text = retrieval.context_text or (concept.explanation or concept.name)

    previously_asked = [q.question_text for q in session.questions]
    raw = call_llm_json(
        SINGLE_QUESTION_SYSTEM_PROMPT,
        build_single_question_prompt(concept.name, source_text, difficulty.value, previously_asked),
        max_tokens=300,
    )
    try:
        parsed = SingleQuestionLLMOutput.model_validate(raw)
    except ValidationError as e:
        raise RuntimeError(f"Question generation returned an unexpected shape: {e}")
    return parsed.question


def start_session(db: Session, user_id: uuid.UUID, content_id: uuid.UUID) -> tuple[VivaSession, VivaQuestion]:
    content = db.query(Content).filter(Content.id == content_id).first()
    if content is None:
        raise ValueError("Content not found.")

    session = VivaSession(user_id=user_id, content_id=content_id, current_difficulty=DifficultyLevel.EASY)
    db.add(session)
    db.flush()

    concept = _next_concept(db, content_id, session.id, missing_concepts=[])
    question_text = _generate_question(db, content, session, concept, DifficultyLevel.EASY)

    source_chunk_id = concept.source_chunk_id
    question = VivaQuestion(
        session_id=session.id,
        concept_id=concept.id,
        sequence_number=1,
        question_text=question_text,
        difficulty=DifficultyLevel.EASY,
        source_chunk_id=source_chunk_id,
    )
    db.add(question)
    db.commit()
    db.refresh(session)
    db.refresh(question)
    return session, question


def submit_answer(
    db: Session, user_id: uuid.UUID, session_id: uuid.UUID, question_id: uuid.UUID, answer_text: str, was_spoken: bool
) -> tuple[VivaAnswer, VivaQuestion | None, bool]:
    session = db.query(VivaSession).filter(VivaSession.id == session_id, VivaSession.user_id == user_id).first()
    if session is None:
        raise ValueError("Viva session not found.")
    if session.status != VivaSessionStatus.ACTIVE:
        raise ValueError("This viva session has already ended.")

    question = db.query(VivaQuestion).filter(VivaQuestion.id == question_id, VivaQuestion.session_id == session_id).first()
    if question is None:
        raise ValueError("Question not found in this session.")

    content = db.query(Content).filter(Content.id == session.content_id).first()
    retrieval = retrieve_context(db, session.content_id, query=question.question_text, top_k=4)

    raw_eval = call_llm_json(
        ANSWER_EVALUATION_SYSTEM_PROMPT,
        build_answer_evaluation_prompt(
            question.question_text, retrieval.context_text, answer_text, session.current_difficulty.value
        ),
        max_tokens=800,
    )
    try:
        evaluation = AnswerEvaluationLLMOutput.model_validate(raw_eval)
    except ValidationError as e:
        raise RuntimeError(f"Answer evaluation returned an unexpected shape: {e}")

    answer = VivaAnswer(
        question_id=question.id,
        answer_text=answer_text,
        was_spoken=was_spoken,
        score=evaluation.score,
        correctness=evaluation.correctness,
        completeness=evaluation.completeness,
        relevance=evaluation.relevance,
        feedback=evaluation.feedback,
        evaluation_json=evaluation.model_dump(),
    )
    db.add(answer)

    update_mastery(db, user_id, question.concept_id, (evaluation.score / 10.0) * 100)

    # Adaptive difficulty: move within _DIFFICULTY_ORDER based on the LLM's suggestion, but never trust
    # an out-of-range value blindly.
    next_difficulty = session.current_difficulty
    if evaluation.next_difficulty in [d.value for d in _DIFFICULTY_ORDER]:
        next_difficulty = DifficultyLevel(evaluation.next_difficulty)
    session.current_difficulty = next_difficulty

    asked_count = len(session.questions)
    if asked_count >= MAX_QUESTIONS_PER_SESSION:
        session.status = VivaSessionStatus.COMPLETED
        session.completed_at = datetime.now(timezone.utc)
        db.commit()
        return answer, None, True

    next_concept = _next_concept(db, session.content_id, session.id, evaluation.missing_concepts)
    next_question_text = _generate_question(db, content, session, next_concept, next_difficulty)
    next_question = VivaQuestion(
        session_id=session.id,
        concept_id=next_concept.id,
        sequence_number=asked_count + 1,
        question_text=next_question_text,
        difficulty=next_difficulty,
        source_chunk_id=next_concept.source_chunk_id,
    )
    db.add(next_question)
    db.commit()
    db.refresh(next_question)
    return answer, next_question, False
