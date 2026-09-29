QUESTION_CHAIN_SYSTEM_PROMPT = """You are a viva examiner creating exam questions strictly grounded in the \
provided source content — never generic questions unrelated to it.

Given one concept and its supporting source content, generate a question CHAIN of increasing difficulty \
(not a random list): each question should build on the understanding tested by the previous one.

Return JSON:
{
  "easy": "a basic definitional/recall question",
  "medium": "a question requiring explanation of why/how",
  "hard": "a question requiring application, design, or critical analysis",
  "follow_up": "a question that probes a common misconception or edge case",
  "expected_answer_points": ["key point the ideal answer should cover", ...],
  "common_mistakes": ["a mistake students commonly make on this topic", ...]
}"""


def build_question_chain_prompt(concept_name: str, source_content: str) -> str:
    return (
        f"Concept: {concept_name}\n\n"
        f"<source_content>\n{source_content}\n</source_content>\n\n"
        "Generate the question chain JSON now."
    )


SINGLE_QUESTION_SYSTEM_PROMPT = """You are an AI viva examiner conducting a live oral exam. Generate exactly \
ONE question at the requested difficulty, grounded in the provided source content, targeting the given concept. \
Do not repeat any question already asked in this session (listed below).

Return JSON: {"question": "..."}"""


def build_single_question_prompt(
    concept_name: str, source_content: str, difficulty: str, previously_asked: list[str]
) -> str:
    asked = "\n".join(f"- {q}" for q in previously_asked) or "(none yet)"
    return (
        f"Concept to test: {concept_name}\n"
        f"Difficulty: {difficulty}\n\n"
        f"<source_content>\n{source_content}\n</source_content>\n\n"
        f"Questions already asked this session:\n{asked}\n\n"
        "Generate the next question JSON now."
    )
