REVISION_SCRIPT_SYSTEM_PROMPT = """You are writing a short micro-learning revision script that condenses a \
lecture into its most important points, to be read aloud over a short video.

Return JSON: {"scenes": [{"concept": "...", "narration": "1-2 sentence spoken narration", \
"subtitle_text": "shorter on-screen text version of the narration"}]}

Pick the 4-8 most important concepts only — this must stay SHORT (a 60-90 second revision video), not a full \
re-teaching. Base every scene strictly on the source content."""


def build_revision_script_prompt(source_content: str) -> str:
    return f"<source_content>\n{source_content}\n</source_content>\n\nGenerate the revision script JSON now."
