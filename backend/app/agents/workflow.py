from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from app.agents.state import AgentState

from app.services.document_parser import (
    parse_document,
)

from app.services.chunker import (
    chunk_pages,
)

from app.services.llm_service import (
    extract_facts,
)


def ingest_document(
    state: AgentState,
) -> AgentState:

    pages = parse_document(
        state["file_path"]
    )

    chunks = chunk_pages(
        pages
    )

    return {
        **state,
        "pages": pages,
        "chunks": chunks,
    }


def classify_document(
    state: AgentState,
) -> AgentState:

    filename = state[
        "filename"
    ].lower()

    if "invoice" in filename:

        document_type = "invoice"

    elif "amendment" in filename:

        document_type = (
            "contract_amendment"
        )

    elif "contract" in filename:

        document_type = "contract"

    else:

        document_type = "unknown"

    return {
        **state,
        "document_type": document_type,
    }


def extract_document_facts(
    state: AgentState,
) -> AgentState:

    document_text = "\n\n".join(

        f"""
--- PAGE {chunk["page_number"]} ---

{chunk["content"]}
"""

        for chunk in state["chunks"]
    )

    result = extract_facts(
        document_text
    )

    facts = [
        fact.model_dump()
        for fact in result.facts
    ]

    return {
        **state,
        "extracted_facts": facts,
    }


def generate_report(
    state: AgentState,
) -> AgentState:

    lines = [

        "# Vendor Contract Intelligence Report",

        "",

        f"Document: {state['filename']}",

        f"Document Type: "
        f"{state['document_type']}",

        "",

        "## Extracted Facts",

        "",
    ]

    facts = state.get(
        "extracted_facts",
        [],
    )

    if not facts:

        lines.append(
            "No supported facts were extracted."
        )

    for index, fact in enumerate(
        facts,
        start=1,
    ):

        evidence = fact[
            "evidence"
        ]

        lines.extend(
            [

                f"### {index}. "
                f"{fact['fact_type']}",

                "",

                f"**Value:** "
                f"{fact['value']}",

                "",

                f"**Confidence:** "
                f"{fact['confidence']:.2f}",

                "",

                "**Evidence:**",

                f"> {evidence['quote']}",

                "",

                f"**Source page:** "
                f"{evidence['page']}",

                "",
            ]
        )

    report = "\n".join(
        lines
    )

    return {
        **state,
        "report": report,
    }


def build_graph():

    graph = StateGraph(
        AgentState
    )

    graph.add_node(
        "ingest",
        ingest_document,
    )

    graph.add_node(
        "classify",
        classify_document,
    )

    graph.add_node(
        "extract",
        extract_document_facts,
    )

    graph.add_node(
        "report",
        generate_report,
    )

    graph.add_edge(
        START,
        "ingest",
    )

    graph.add_edge(
        "ingest",
        "classify",
    )

    graph.add_edge(
        "classify",
        "extract",
    )

    graph.add_edge(
        "extract",
        "report",
    )

    graph.add_edge(
        "report",
        END,
    )

    return graph.compile()