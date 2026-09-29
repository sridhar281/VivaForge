import uuid

from app.models.concept import Concept, ConceptMastery
from app.models.content import Content, ContentType, ProcessingStatus
from app.models.user import User
from app.services.knowledge_gap_service import generate_revision_plan, get_knowledge_profile
from app.utils.security import hash_password


def _make_user(db):
    user = User(email="gaptest@example.com", hashed_password=hash_password("whatever123"))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _make_content_with_concepts(db, owner_id, concept_names):
    content = Content(
        owner_id=owner_id,
        title="Test Lecture",
        content_type=ContentType.PDF,
        original_filename="lecture.pdf",
        storage_path="/tmp/lecture.pdf",
        file_size_bytes=1000,
        status=ProcessingStatus.COMPLETED,
    )
    db.add(content)
    db.flush()

    concepts = []
    for name in concept_names:
        c = Concept(content_id=content.id, name=name, explanation="test")
        db.add(c)
        concepts.append(c)
    db.commit()
    for c in concepts:
        db.refresh(c)
    return content, concepts


def test_knowledge_profile_classifies_strong_weak_unseen(db_session):
    user = _make_user(db_session)
    _content, concepts = _make_content_with_concepts(db_session, user.id, ["Normalization", "ACID", "Indexing"])

    db_session.add(ConceptMastery(user_id=user.id, concept_id=concepts[0].id, mastery_score=30, attempts=1))  # weak
    db_session.add(ConceptMastery(user_id=user.id, concept_id=concepts[1].id, mastery_score=90, attempts=2))  # strong
    # concepts[2] (Indexing) never attempted -> unseen
    db_session.commit()

    profile = get_knowledge_profile(db_session, user.id)

    assert [c["concept_name"] for c in profile["weak_concepts"]] == ["Normalization"]
    assert [c["concept_name"] for c in profile["strong_concepts"]] == ["ACID"]
    assert [c["concept_name"] for c in profile["unseen_concepts"]] == ["Indexing"]


def test_revision_plan_prioritizes_weakest_concepts_first(db_session):
    user = _make_user(db_session)
    _content, concepts = _make_content_with_concepts(db_session, user.id, ["A", "B", "C"])

    db_session.add(ConceptMastery(user_id=user.id, concept_id=concepts[0].id, mastery_score=45, attempts=1))
    db_session.add(ConceptMastery(user_id=user.id, concept_id=concepts[1].id, mastery_score=10, attempts=1))
    db_session.add(ConceptMastery(user_id=user.id, concept_id=concepts[2].id, mastery_score=95, attempts=1))
    db_session.commit()

    plan = generate_revision_plan(db_session, user.id)

    names = [item["concept_name"] for item in plan.items_json]
    assert names[0] == "B"  # lowest score (10) comes first
    assert "C" not in names  # strong concept excluded entirely


def test_revision_plan_marks_previous_plan_not_current(db_session):
    user = _make_user(db_session)
    _make_content_with_concepts(db_session, user.id, ["Solo Concept"])

    first_plan = generate_revision_plan(db_session, user.id)
    second_plan = generate_revision_plan(db_session, user.id)

    db_session.refresh(first_plan)
    assert first_plan.is_current is False
    assert second_plan.is_current is True
