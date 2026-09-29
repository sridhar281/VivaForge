export type Difficulty = "easy" | "medium" | "hard";

export interface QuestionRead {
  id: string;
  question_text: string;
  difficulty: Difficulty;
  sequence_number: number;
  source_label: string | null;
}

export interface SessionStartResponse {
  session_id: string;
  status: string;
  first_question: QuestionRead;
}

export interface EvaluationRead {
  score: number;
  correctness: number;
  completeness: number;
  relevance: number;
  correct_concepts: string[];
  missing_concepts: string[];
  incorrect_claims: string[];
  unsupported_claims: string[];
  feedback: string;
}

export interface AnswerSubmitResponse {
  evaluation: EvaluationRead;
  session_completed: boolean;
  next_question: QuestionRead | null;
}

export interface ConceptScore {
  concept_id: string;
  concept_name: string;
  mastery_score: number | null;
}

export interface KnowledgeProfile {
  strong_concepts: ConceptScore[];
  weak_concepts: ConceptScore[];
  unseen_concepts: ConceptScore[];
}

export interface RevisionPlanItem {
  concept_id: string;
  concept_name: string;
  mastery_score: number | null;
  estimated_minutes: number;
}

export interface RevisionPlan {
  id: string;
  items: RevisionPlanItem[];
  estimated_minutes: number;
  created_at: string;
}

export interface ExplainBackPrompt {
  concept_id: string;
  concept_name: string;
  prompt_text: string;
}

export interface ExplainBackResult {
  covered_points: string[];
  missing_points: string[];
  incorrect_points: string[];
  mastery_percent: number;
  recommendation: string;
}
