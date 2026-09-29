EXPLAIN_BACK_SYSTEM_PROMPT = """The student was asked to explain a concept in their own words, unprompted by \
specific questions. Compare their explanation against the source-grounded concept knowledge.

Return JSON exactly:
{
  "covered_points": ["point from the source the explanation correctly conveyed", ...],
  "missing_points": ["important point from the source the explanation omitted", ...],
  "incorrect_points": ["a specific claim in the explanation that contradicts the source", ...],
  "mastery_percent": <float 0-100, overall grasp of this concept>,
  "recommendation": "one short sentence: what to review next, e.g. 'Review Normalization -> 2NF'"
}

Judge understanding, not phrasing — a correct explanation in different words still counts as covered."""


def build_explain_back_prompt(concept_name: str, source_content: str, user_explanation: str) -> str:
    return (
        f"Concept: {concept_name}\n\n"
        f"<source_content>\n{source_content}\n</source_content>\n\n"
        f"<user_answer>\n{user_explanation}\n</user_answer>\n\n"
        "Evaluate this explanation now."
    )
