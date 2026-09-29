"""
Builds the viva-prep PDF described in section 12. Takes already-generated
data (summary + per-concept question chains) and lays it out — no LLM
calls happen in this file, keeping generation and rendering separate.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

styles = getSampleStyleSheet()
_title_style = ParagraphStyle("VFTitle", parent=styles["Title"], spaceAfter=18)
_h2 = ParagraphStyle("VFH2", parent=styles["Heading2"], spaceBefore=14, spaceAfter=8)
_h3 = ParagraphStyle("VFH3", parent=styles["Heading3"], spaceBefore=10, spaceAfter=6)
_body = ParagraphStyle("VFBody", parent=styles["BodyText"], spaceAfter=6)


def generate_viva_pdf(
    output_path: str,
    content_title: str,
    executive_summary: str,
    key_concepts: list[str],
    definitions: list[dict],
    question_chains: list[dict],  # [{"concept": str, "easy":..., "medium":..., "hard":..., "follow_up":...,
    #                                 "expected_answer_points": [...], "common_mistakes": [...]}]
) -> str:
    doc = SimpleDocTemplate(output_path, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    story = []

    # 1. Title
    story.append(Paragraph(f"Viva Preparation: {content_title}", _title_style))

    # 2. Content overview
    story.append(Paragraph("Content Overview", _h2))
    story.append(Paragraph(executive_summary, _body))

    # 3. Important concepts
    story.append(Paragraph("Important Concepts", _h2))
    for c in key_concepts:
        story.append(Paragraph(f"&bull; {c}", _body))

    # 4. Definitions
    if definitions:
        story.append(Paragraph("Definitions", _h2))
        for d in definitions:
            story.append(Paragraph(f"<b>{d['term']}</b>: {d['definition']}", _body))

    story.append(PageBreak())

    # 5-8: viva questions by difficulty, 9: follow-ups, 10: expected answers, 11: common mistakes — per concept
    story.append(Paragraph("Viva Questions", _h2))
    for chain in question_chains:
        story.append(Paragraph(chain["concept"], _h3))
        story.append(Paragraph(f"<b>Easy:</b> {chain['easy']}", _body))
        story.append(Paragraph(f"<b>Medium:</b> {chain['medium']}", _body))
        story.append(Paragraph(f"<b>Hard:</b> {chain['hard']}", _body))
        story.append(Paragraph(f"<b>Follow-up:</b> {chain['follow_up']}", _body))

        if chain.get("expected_answer_points"):
            story.append(Paragraph("Expected answer should cover:", _body))
            for point in chain["expected_answer_points"]:
                story.append(Paragraph(f"&bull; {point}", _body))

        if chain.get("common_mistakes"):
            story.append(Paragraph("Common mistakes:", _body))
            for m in chain["common_mistakes"]:
                story.append(Paragraph(f"&bull; {m}", _body))

        story.append(Spacer(1, 10))

    # 12. Quick revision sheet + source references
    story.append(PageBreak())
    story.append(Paragraph("Quick Revision Sheet", _h2))
    for c in key_concepts:
        story.append(Paragraph(f"&bull; {c}", _body))

    doc.build(story)
    return output_path
