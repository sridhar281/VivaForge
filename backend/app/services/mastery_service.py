import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.concept import ConceptMastery


def update_mastery(db: Session, user_id: uuid.UUID, concept_id: uuid.UUID | None, score_percent: float) -> None:
    """score_percent is 0-100. Blends into a running average rather than overwriting,
    so one lucky/unlucky attempt doesn't swing the dashboard wildly."""
    if concept_id is None:
        return
    record = (
        db.query(ConceptMastery)
        .filter(ConceptMastery.user_id == user_id, ConceptMastery.concept_id == concept_id)
        .first()
    )
    if record is None:
        record = ConceptMastery(user_id=user_id, concept_id=concept_id, mastery_score=score_percent, attempts=1)
        db.add(record)
    else:
        record.mastery_score = round((record.mastery_score * record.attempts + score_percent) / (record.attempts + 1), 1)
        record.attempts += 1
    record.last_evaluated_at = datetime.now(timezone.utc)
    db.commit()
