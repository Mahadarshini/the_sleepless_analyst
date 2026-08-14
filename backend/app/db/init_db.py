from sqlalchemy import text

from app.db.database import Base, engine
from app.models.document import Document, DocumentChunk


def init_database():
    with engine.begin() as connection:
        connection.execute(
            text("CREATE EXTENSION IF NOT EXISTS vector")
        )

    Base.metadata.create_all(
        bind=engine
    )