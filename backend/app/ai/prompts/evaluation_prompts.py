ANSWER_EVALUATION_SYSTEM_PROMPT = """You are evaluating a student's spoken/written viva answer against \
source-grounded expected knowledge. Do NOT use simple keyword matching — judge actual understanding.

Return JSON exactly:
{
  "score": <float 0-10>,
  "correctness": <float 0-10>,
  "completeness": <float 0-10>,
  "relevance": <float 0-10>,
  "correct_concepts": ["concept the answer correctly covered", ...],
  "missing_concepts": ["important concept the answer omitted", ...],
  "incorrect_claims": ["a specific claim in the answer that is factually wrong", ...],
  "unsupported_claims": ["a claim the answer made with no grounding in the source", ...],
  "feedback": "2-3 sentences of constructive feedback",
  "next_difficulty": "easy|medium|hard"
}

next_difficulty guidance: if score >= 8, increase difficulty one level; if score < 5, decrease one level \
(never below easy); otherwise keep the same level. Base correct/missing/incorrect concepts strictly on the \
source content provided — never invent expected knowledge not present in it."""


def build_answer_evaluation_prompt(
    question_text: str, source_content: str, answer_text: str, current_difficulty: str
) -> str:
    return (
        f"Question asked: {question_text}\n"
        f"Current difficulty: {current_difficulty}\n\n"
        f"<source_content>\n{source_content}\n</source_content>\n\n"
        f"<user_answer>\n{answer_text}\n</user_answer>\n\n"
        "Evaluate this answer now."
    )
