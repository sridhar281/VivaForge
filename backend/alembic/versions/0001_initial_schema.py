"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-09-13

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Enum type definitions, shared between upgrade/downgrade.
# create_type=False is required here: without it, SQLAlchemy tries to
# auto-create each enum type a SECOND time the moment it sees a column
# that uses it (inside op.create_table below) -- even though we already
# create it explicitly a few lines into upgrade(). That double-creation
# is what causes 'type already exists' on every run. We create each type
# exactly once, explicitly, with checkfirst=True.
content_type_enum = postgresql.ENUM("video", "audio", "pdf", "pptx", name="contenttype", create_type=False)
processing_status_enum = postgresql.ENUM(
    "uploaded", "processing", "transcribing", "understanding", "generating", "completed", "failed",
    name="processingstatus", create_type=False,
)
relation_type_enum = postgresql.ENUM(
    "prerequisite", "related_to", "part_of", "example_of", "depends_on", name="relationtype", create_type=False
)
difficulty_enum = postgresql.ENUM("easy", "medium", "hard", name="difficultylevel", create_type=False)
viva_session_status_enum = postgresql.ENUM(
    "active", "completed", "expired", name="vivasessionstatus", create_type=False
)
artifact_type_enum = postgresql.ENUM(
    "summary_json", "viva_pdf", "flashcard_set", "revision_video", "knowledge_graph_json",
    name="artifacttype", create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    content_type_enum.create(bind, checkfirst=True)
    processing_status_enum.create(bind, checkfirst=True)
    relation_type_enum.create(bind, checkfirst=True)
    difficulty_enum.create(bind, checkfirst=True)
    viva_session_status_enum.create(bind, checkfirst=True)
    artifact_type_enum.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "contents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("content_type", content_type_enum, nullable=False),
        sa.Column("original_filename", sa.String(500), nullable=False),
        sa.Column("storage_path", sa.String(1000), nullable=False),
        sa.Column("file_size_bytes", sa.Integer, nullable=False),
        sa.Column("status", processing_status_enum, nullable=False, server_default="uploaded"),
        sa.Column("status_message", sa.Text, nullable=True),
        sa.Column("duration_seconds", sa.Float, nullable=True),
        sa.Column("page_count", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "content_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("content_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("contents.id"), nullable=False),
        sa.Column("chunk_index", sa.Integer, nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("topic_label", sa.String(255), nullable=True),
        sa.Column("start_time_seconds", sa.Float, nullable=True),
        sa.Column("end_time_seconds", sa.Float, nullable=True),
        sa.Column("page_number", sa.Integer, nullable=True),
        sa.Column("embedded", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "concepts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("content_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("contents.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("explanation", sa.Text, nullable=True),
        sa.Column(
            "source_chunk_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("content_chunks.id"), nullable=True
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "concept_edges",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_concept_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("concepts.id"), nullable=False),
        sa.Column("target_concept_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("concepts.id"), nullable=False),
        sa.Column("relation_type", relation_type_enum, nullable=False),
        sa.UniqueConstraint("source_concept_id", "target_concept_id", "relation_type"),
    )

    op.create_table(
        "concept_mastery",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("concept_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("concepts.id"), nullable=False),
        sa.Column("mastery_score", sa.Float, nullable=False, server_default="0"),
        sa.Column("attempts", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_evaluated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "concept_id"),
    )

    op.create_table(
        "viva_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("content_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("contents.id"), nullable=False),
        sa.Column("status", viva_session_status_enum, nullable=False, server_default="active"),
        sa.Column("current_difficulty", difficulty_enum, nullable=False, server_default="easy"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "viva_questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("viva_sessions.id"), nullable=False
        ),
        sa.Column("concept_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("concepts.id"), nullable=True),
        sa.Column("sequence_number", sa.Integer, nullable=False),
        sa.Column("question_text", sa.Text, nullable=False),
        sa.Column("difficulty", difficulty_enum, nullable=False),
        sa.Column(
            "source_chunk_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("content_chunks.id"), nullable=True
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "viva_answers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "question_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("viva_questions.id"), nullable=False
        ),
        sa.Column("answer_text", sa.Text, nullable=False),
        sa.Column("was_spoken", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("score", sa.Float, nullable=True),
        sa.Column("correctness", sa.Float, nullable=True),
        sa.Column("completeness", sa.Float, nullable=True),
        sa.Column("relevance", sa.Float, nullable=True),
        sa.Column("feedback", sa.Text, nullable=True),
        sa.Column("evaluation_json", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "artifacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("content_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("contents.id"), nullable=False),
        sa.Column("artifact_type", artifact_type_enum, nullable=False),
        sa.Column("storage_path", sa.String(1000), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "revision_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("items_json", sa.JSON, nullable=False),
        sa.Column("estimated_minutes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_current", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("revision_plans")
    op.drop_table("artifacts")
    op.drop_table("viva_answers")
    op.drop_table("viva_questions")
    op.drop_table("viva_sessions")
    op.drop_table("concept_mastery")
    op.drop_table("concept_edges")
    op.drop_table("concepts")
    op.drop_table("content_chunks")
    op.drop_table("contents")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    bind = op.get_bind()
    artifact_type_enum.drop(bind, checkfirst=True)
    viva_session_status_enum.drop(bind, checkfirst=True)
    difficulty_enum.drop(bind, checkfirst=True)
    relation_type_enum.drop(bind, checkfirst=True)
    processing_status_enum.drop(bind, checkfirst=True)
    content_type_enum.drop(bind, checkfirst=True)
