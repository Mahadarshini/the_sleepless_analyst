from pathlib import Path

from pypdf import PdfReader
from docx import Document as DocxDocument


def parse_document(file_path: str) -> list[dict]:
    path = Path(file_path)

    if path.suffix.lower() == ".pdf":
        return parse_pdf(path)

    if path.suffix.lower() == ".docx":
        return parse_docx(path)

    if path.suffix.lower() == ".txt":
        return parse_txt(path)

    raise ValueError(
        f"Unsupported document format: {path.suffix}"
    )


def parse_pdf(path: Path) -> list[dict]:
    reader = PdfReader(str(path))

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        pages.append(
            {
                "page_number": page_number,
                "text": text.strip(),
            }
        )

    return pages


def parse_docx(path: Path) -> list[dict]:
    document = DocxDocument(str(path))

    text = "\n".join(
        paragraph.text
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    )

    return [
        {
            "page_number": None,
            "text": text,
        }
    ]


def parse_txt(path: Path) -> list[dict]:
    text = path.read_text(
        encoding="utf-8"
    )

    return [
        {
            "page_number": None,
            "text": text,
        }
    ]