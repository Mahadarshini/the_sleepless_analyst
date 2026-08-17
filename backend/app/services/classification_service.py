def classify_document(
    filename: str,
) -> str:

    name = filename.lower()

    if "invoice" in name:
        return "invoice"

    if "amendment" in name:
        return "contract_amendment"

    if "contract" in name:
        return "contract"

    return "unknown"