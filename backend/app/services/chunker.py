def chunk_pages(
    pages: list[dict],
    chunk_size: int = 1000,
) -> list[dict]:

    chunks = []

    for page in pages:
        text = page["text"]

        if not text:
            continue

        for start in range(0, len(text), chunk_size):
            chunk_text = text[start:start + chunk_size]

            chunks.append(
                {
                    "page_number": page["page_number"],
                    "content": chunk_text,
                }
            )

    return chunks