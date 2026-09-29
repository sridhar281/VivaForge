"""
Cross-dialect UUID type.

Models are written against Postgres in production, but tests (Phase 2's
auth tests included) run against an in-memory SQLite engine for speed —
and SQLite has no native UUID type. `sqlalchemy.dialects.postgresql.UUID`
only compiles on Postgres, so importing it directly in models breaks
SQLite-backed tests. This TypeDecorator picks the right underlying
representation per dialect automatically.

Standard recipe, see:
https://docs.sqlalchemy.org/en/20/core/custom_types.html#backend-agnostic-guid-type
"""
import uuid

from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.types import CHAR, TypeDecorator


class GUID(TypeDecorator):
    """Platform-independent UUID type. Stores as PG native UUID, else CHAR(32) hex string."""

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            return str(value)
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(value)
        return value.hex

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(value)
