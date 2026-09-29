import pytest
from pydantic import ValidationError

from app.schemas.ai_outputs import (
    AnswerEvaluationLLMOutput,
    ConceptExtractionLLMOutput,
    SummaryLLMOutput,
)


def test_summary_output_accepts_well_formed_json():
    valid = {
        "executive_summary": "A short overview.",
        "topic_summaries": [{"topic": "Intro", "summary": "Covers basics."}],
        "key_concepts": ["ACID", "Normalization"],
        "definitions": [{"term": "ACID", "definition": "A set of DB transaction properties."}],
        "examples": ["A bank transfer is a classic ACID example."],
        "quick_revision_notes": ["ACID = Atomicity, Consistency, Isolation, Durability"],
    }
    parsed = SummaryLLMOutput.model_validate(valid)
    assert parsed.executive_summary == "A short overview."


def test_summary_output_rejects_missing_required_field():
    missing_key_concepts = {
        "executive_summary": "A short overview.",
        "topic_summaries": [],
        "definitions": [],
        "examples": [],
        "quick_revision_notes": [],
    }
    with pytest.raises(ValidationError):
        SummaryLLMOutput.model_validate(missing_key_concepts)


def test_concept_extraction_rejects_wrong_types():
    bad = {"concepts": "this should be a list, not a string", "relationships": []}
    with pytest.raises(ValidationError):
        ConceptExtractionLLMOutput.model_validate(bad)


def test_answer_evaluation_defaults_optional_lists():
    minimal = {
        "score": 7.5,
        "correctness": 8,
        "completeness": 6,
        "relevance": 9,
        "feedback": "Good answer overall.",
        "next_difficulty": "medium",
    }
    parsed = AnswerEvaluationLLMOutput.model_validate(minimal)
    assert parsed.correct_concepts == []
    assert parsed.missing_concepts == []


def test_answer_evaluation_rejects_non_numeric_score():
    bad = {
        "score": "seven and a half",
        "correctness": 8,
        "completeness": 6,
        "relevance": 9,
        "feedback": "...",
        "next_difficulty": "medium",
    }
    with pytest.raises(ValidationError):
        AnswerEvaluationLLMOutput.model_validate(bad)
