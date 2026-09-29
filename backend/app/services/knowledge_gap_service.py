import uuid

from sqlalchemy.orm import Session

from app.models.concept import Concept, ConceptMastery
from app.models.content import Content
from app.models.revision import RevisionPlan

STRONG_THRESHOLD = 75
WEAK_THRESHOLD = 50
MINUTES_PER_REVISION_ITEM = 7


def get_knowledge_profile(db: Session, user_id: uuid.UUID) -> dict:
    """
    Aggregates mastery across every piece of content the user owns.
    Returns strong/weak/unseen concept lists — this is what powers the
    dashboard's "Knowledge Mastery" bars (section 6).
    """
    owned_content_ids = [c.id for c in db.query(Content.id).filter(Content.owner_id == user_id)]
    all_concepts = db.query(Concept).filter(Concept.content_id.in_(owned_content_ids)).all() if owned_content_ids else []

    mastery_by_id = {
        m.concept_id: m.mastery_score
        for m in db.query(ConceptMastery).filter(
            ConceptMastery.user_id == user_id, ConceptMastery.concept_id.in_([c.id for c in all_concepts])
        )
    }

    strong, weak, unseen = [], [], []
    for c in all_concepts:
        score = mastery_by_id.get(c.id)
        entry = {"concept_id": c.id, "concept_name": c.name, "mastery_score": score}
        if score is None:
            unseen.append(entry)
        elif score >= STRONG_THRESHOLD:
            strong.append(entry)
        elif score < WEAK_THRESHOLD:
            weak.append(entry)

    return {"strong_concepts": strong, "weak_concepts": weak, "unseen_concepts": unseen}


def generate_revision_plan(db: Session, user_id: uuid.UUID) -> RevisionPlan:
    """
    Weak concepts first, then unseen ones, capped at 5 items so "today's
    revision" stays actually doable (section 17's example shows 3 items /
    20 minutes — we cap similarly rather than dumping every gap at once).
    """
    profile = get_knowledge_profile(db, user_id)
    ranked = sorted(profile["weak_concepts"], key=lambda x: x["mastery_score"]) + profile["unseen_concepts"]
    items = ranked[:5]

    items_json = [
        {
            "concept_id": str(item["concept_id"]),
            "concept_name": item["concept_name"],
            "mastery_score": item["mastery_score"],
            "estimated_minutes": MINUTES_PER_REVISION_ITEM,
        }
        for item in items
    ]

    # Mark any previous plan as no longer current.
    db.query(RevisionPlan).filter(RevisionPlan.user_id == user_id, RevisionPlan.is_current == True).update(  # noqa: E712
        {"is_current": False}
    )

    plan = RevisionPlan(
        user_id=user_id,
        items_json=items_json,
        estimated_minutes=len(items) * MINUTES_PER_REVISION_ITEM,
        is_current=True,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def get_current_plan(db: Session, user_id: uuid.UUID) -> RevisionPlan | None:
    return (
        db.query(RevisionPlan)
        .filter(RevisionPlan.user_id == user_id, RevisionPlan.is_current == True)  # noqa: E712
        .order_by(RevisionPlan.created_at.desc())
        .first()
    )
