FLASHCARD_SYSTEM_PROMPT = """You create flashcards from educational source content for spaced-repetition study.

Return JSON: {"cards": [{"front": "a question or term", "back": "the answer/definition", "concept": "related concept name"}]}

Generate 8-15 cards covering the most important, testable facts in the source. Keep "front" short (a question \
or term) and "back" concise (1-3 sentences). Base every card strictly on the source content."""


def build_flashcard_prompt(source_content: str) -> str:
    return f"<source_content>\n{source_content}\n</source_content>\n\nGenerate the flashcards JSON now."
