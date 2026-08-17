from pathlib import Path

from app.services.document_parser import (
    parse_document,
)

from app.services.chunker import (
    chunk_pages,
)


def process_document(
    file_path: str,
) -> dict:

    pages = parse_document(
        file_path
    )

    chunks = chunk_pages(
        pages
    )

    return {
        "file_path": file_path,
        "filename": Path(file_path).name,
        "pages": pages,
        "chunks": chunks,
    }


def process_documents(
    file_paths: list[str],
) -> list[dict]:

    documents = []

    for file_path in file_paths:

        document = process_document(
            file_path
        )

        documents.append(
            document
        )

    return documents