import uuid

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.concept import Concept, ConceptEdge, ConceptMastery


class GraphNode(BaseModel):
    id: uuid.UUID
    name: str
    explanation: str | None
    mastery_score: float | None  # None = not attempted yet


class GraphEdge(BaseModel):
    source: uuid.UUID
    target: uuid.UUID
    relation_type: str


class GraphRead(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


def build_graph(db: Session, user_id: uuid.UUID, content_id: uuid.UUID) -> GraphRead:
    concepts = db.query(Concept).filter(Concept.content_id == content_id).all()
    concept_ids = [c.id for c in concepts]

    mastery_by_id = {
        m.concept_id: m.mastery_score
        for m in db.query(ConceptMastery).filter(
            ConceptMastery.user_id == user_id, ConceptMastery.concept_id.in_(concept_ids)
        )
    }

    nodes = [
        GraphNode(id=c.id, name=c.name, explanation=c.explanation, mastery_score=mastery_by_id.get(c.id))
        for c in concepts
    ]

    edges_raw = db.query(ConceptEdge).filter(ConceptEdge.source_concept_id.in_(concept_ids)).all()
    edges = [
        GraphEdge(source=e.source_concept_id, target=e.target_concept_id, relation_type=e.relation_type.value)
        for e in edges_raw
    ]

    return GraphRead(nodes=nodes, edges=edges)
