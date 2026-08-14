import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import (
    Document,
    DocumentChunk,
)

from app.services.embedding_service import (
    embed_texts,
)


def get_document_by_hash(
    db: Session,
    content_hash: str,
) -> Document | None:

    return db.scalar(
        select(Document).where(
            Document.content_hash
            == content_hash
        )
    )


def create_document(
    db: Session,
    filename: str,
    content_hash: str,
) -> Document:

    existing = get_document_by_hash(
        db,
        content_hash,
    )

    if existing:
        return existing

    document = Document(
        filename=filename,
        content_hash=content_hash,
        status="processing",
    )

    db.add(document)

    db.commit()

    db.refresh(document)

    return document


def save_chunks(
    db: Session,
    document_id: uuid.UUID,
    chunks: list[dict],
):

    if not chunks:
        return

    texts = [
        chunk["content"]
        for chunk in chunks
    ]

    embeddings = embed_texts(texts)

    for index, (
        chunk,
        embedding,
    ) in enumerate(
        zip(
            chunks,
            embeddings,
        )
    ):

        db_chunk = DocumentChunk(
            document_id=document_id,
            page_number=chunk[
                "page_number"
            ],
            chunk_index=index,
            content=chunk[
                "content"
            ],
            embedding=embedding,
        )

        db.add(db_chunk)

    db.commit()