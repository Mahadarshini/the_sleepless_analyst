import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


EMBEDDING_DIMENSION = 384


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    filename: Mapped[str] = mapped_column(
        String(255)
    )

    document_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    content_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="uploaded",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id"),
        index=True,
    )

    page_number: Mapped[int | None] = mapped_column(
        nullable=True
    )

    chunk_index: Mapped[int] = mapped_column()

    content: Mapped[str] = mapped_column(
        Text
    )

    embedding: Mapped[list | None] = mapped_column(
        Vector(EMBEDDING_DIMENSION),
        nullable=True,
    )