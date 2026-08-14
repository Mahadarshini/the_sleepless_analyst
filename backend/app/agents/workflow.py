from langgraph.graph import StateGraph, START, END

from app.agents.state import AgentState
from app.services.document_parser import parse_document
from app.services.chunker import chunk_pages


def ingest_document(state: AgentState) -> AgentState:

    pages = parse_document(
        state["file_path"]
    )

    chunks = chunk_pages(pages)

    return {
        **state,
        "pages": pages,
        "chunks": chunks,
    }


def classify_document(state: AgentState) -> AgentState:

    filename = state["filename"].lower()

    if "invoice" in filename:
        document_type = "invoice"

    elif "amendment" in filename:
        document_type = "contract_amendment"

    elif "contract" in filename:
        document_type = "contract"

    else:
        document_type = "unknown"

    return {
        **state,
        "document_type": document_type,
    }


def extract_facts(state: AgentState) -> AgentState:

    # Temporary deterministic extraction.
    # We will replace this with the LLM extraction agent.

    facts = []

    for chunk in state["chunks"]:
        text = chunk["content"]

        if "payment" in text.lower():
            facts.append(
                {
                    "fact": "payment_terms_mentioned",
                    "value": True,
                    "page": chunk["page_number"],
                    "evidence": text[:300],
                }
            )

        if "contract value" in text.lower():
            facts.append(
                {
                    "fact": "contract_value_mentioned",
                    "value": True,
                    "page": chunk["page_number"],
                    "evidence": text[:300],
                }
            )

    return {
        **state,
        "extracted_facts": facts,
    }


def generate_report(state: AgentState) -> AgentState:

    lines = [
        f"# Document Report",
        "",
        f"Document: {state['filename']}",
        f"Type: {state['document_type']}",
        "",
        "## Extracted Facts",
    ]

    for fact in state.get("extracted_facts", []):
        lines.append(
            f"- {fact['fact']}: {fact['value']} "
            f"(page {fact['page']})"
        )

    report = "\n".join(lines)

    return {
        **state,
        "report": report,
    }


def build_graph():

    graph = StateGraph(AgentState)

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
        extract_facts,
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