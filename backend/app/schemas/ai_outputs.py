from pydantic import BaseModel, Field


class TopicSummaryItem(BaseModel):
    topic: str
    summary: str


class DefinitionItem(BaseModel):
    term: str
    definition: str


class SummaryLLMOutput(BaseModel):
    executive_summary: str
    topic_summaries: list[TopicSummaryItem]
    key_concepts: list[str]
    definitions: list[DefinitionItem]
    examples: list[str]
    quick_revision_notes: list[str]


class ConceptItem(BaseModel):
    name: str
    explanation: str


class RelationshipItem(BaseModel):
    source: str
    target: str
    type: str


class ConceptExtractionLLMOutput(BaseModel):
    concepts: list[ConceptItem]
    relationships: list[RelationshipItem] = Field(default_factory=list)


class QuestionChainLLMOutput(BaseModel):
    easy: str
    medium: str
    hard: str
    follow_up: str
    expected_answer_points: list[str]
    common_mistakes: list[str]


class SingleQuestionLLMOutput(BaseModel):
    question: str


class AnswerEvaluationLLMOutput(BaseModel):
    score: float
    correctness: float
    completeness: float
    relevance: float
    correct_concepts: list[str] = Field(default_factory=list)
    missing_concepts: list[str] = Field(default_factory=list)
    incorrect_claims: list[str] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)
    feedback: str
    next_difficulty: str


class ExplainBackLLMOutput(BaseModel):
    covered_points: list[str] = Field(default_factory=list)
    missing_points: list[str] = Field(default_factory=list)
    incorrect_points: list[str] = Field(default_factory=list)
    mastery_percent: float
    recommendation: str


class FlashcardItem(BaseModel):
    front: str
    back: str
    concept: str


class FlashcardSetLLMOutput(BaseModel):
    cards: list[FlashcardItem]


class RevisionSceneItem(BaseModel):
    concept: str
    narration: str
    subtitle_text: str


class RevisionScriptLLMOutput(BaseModel):
    scenes: list[RevisionSceneItem]
