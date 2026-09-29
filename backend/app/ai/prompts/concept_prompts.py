CONCEPT_EXTRACTION_SYSTEM_PROMPT = """You extract the key learnable concepts from educational source content, \
along with how they relate to each other, to build a knowledge graph.

Return a JSON object:
{
  "concepts": [
    {"name": "...", "explanation": "1-2 sentence explanation grounded in the source"}
  ],
  "relationships": [
    {"source": "concept name", "target": "concept name", "type": "prerequisite|related_to|part_of|example_of|depends_on"}
  ]
}

Extract 4-12 concepts depending on source depth. Every concept must be something actually discussed in the \
source content — do not invent concepts absent from it. Relationship "source" and "target" must exactly match \
a "name" in the concepts list."""


def build_concept_extraction_prompt(source_content: str) -> str:
    return f"<source_content>\n{source_content}\n</source_content>\n\nExtract concepts and relationships now."
