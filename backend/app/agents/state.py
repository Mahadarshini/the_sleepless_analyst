from typing import TypedDict


class AgentState(TypedDict, total=False):
    run_id: str

    document_id: str
    file_path: str
    filename: str

    document_type: str

    pages: list
    chunks: list

    extracted_facts: list

    report: str

    errors: list