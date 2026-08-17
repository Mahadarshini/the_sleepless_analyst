from typing import TypedDict


class AgentState(TypedDict, total=False):

    run_id: str

    document_ids: list[str]

    file_paths: list[str]

    filenames: list[str]

    documents: list[dict]

    extracted_facts: list[dict]

    normalized_facts: list[dict]

    conflicts: list[dict]

    report: str

    errors: list