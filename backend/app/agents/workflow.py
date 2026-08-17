from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from app.agents.state import AgentState

from app.services.document_pipeline import (
    process_documents,
)

from app.services.classification_service import (
    classify_document,
)

from app.services.llm_service import (
    extract_facts,
)


def ingest_documents(
    state: AgentState,
) -> AgentState:

    documents = process_documents(
        state["file_paths"]
    )

    for document in documents:

        document["document_type"] = (
            classify_document(
                document["filename"]
            )
        )

    return {
        **state,
        "documents": documents,
    }


def extract_document_facts(
    state: AgentState,
) -> AgentState:

    all_facts = []

    for document in state["documents"]:

        document_text = "\n\n".join(

            f"""
--- PAGE {chunk["page_number"]} ---

{chunk["content"]}
"""

            for chunk in document["chunks"]
        )

        result = extract_facts(
            document_text
        )

        for fact in result.facts:

            fact_data = (
                fact.model_dump()
            )

            fact_data[
                "filename"
            ] = document["filename"]

            fact_data[
                "document_type"
            ] = document[
                "document_type"
            ]

            all_facts.append(
                fact_data
            )

    return {
        **state,
        "extracted_facts": all_facts,
    }


def normalize_facts(
    state: AgentState,
) -> AgentState:

    normalized = []

    for fact in state[
        "extracted_facts"
    ]:

        normalized.append(
            {
                "fact_type": (
                    fact["fact_type"]
                    .strip()
                    .lower()
                ),
                "value": (
                    fact["value"]
                    .strip()
                ),
                "confidence": (
                    fact["confidence"]
                ),
                "filename": (
                    fact["filename"]
                ),
                "document_type": (
                    fact["document_type"]
                ),
                "evidence": (
                    fact["evidence"]
                ),
            }
        )

    return {
        **state,
        "normalized_facts": normalized,
    }


def detect_conflicts(
    state: AgentState,
) -> AgentState:

    facts = state[
        "normalized_facts"
    ]

    conflicts = []

    grouped = {}

    for fact in facts:

        fact_type = fact[
            "fact_type"
        ]

        grouped.setdefault(
            fact_type,
            []
        ).append(fact)

    for fact_type, values in grouped.items():

        unique_values = set(
            fact["value"]
            for fact in values
        )

        if len(unique_values) <= 1:
            continue

        conflicts.append(
            {
                "fact_type": fact_type,
                "values": values,
            }
        )

    return {
        **state,
        "conflicts": conflicts,
    }


def generate_report(
    state: AgentState,
) -> AgentState:

    lines = [

        "# Vendor Contract Intelligence Report",

        "",

        "## Documents",

        "",
    ]

    for document in state[
        "documents"
    ]:

        lines.append(
            f"- {document['filename']} "
            f"({document['document_type']})"
        )

    lines.extend(
        [
            "",
            "## Extracted Facts",
            "",
        ]
    )

    for fact in state[
        "normalized_facts"
    ]:

        evidence = fact[
            "evidence"
        ]

        lines.extend(
            [
                f"### {fact['fact_type']}",
                "",
                f"**Value:** "
                f"{fact['value']}",
                "",
                f"**Source:** "
                f"{fact['filename']}",
                "",
                f"**Confidence:** "
                f"{fact['confidence']:.2f}",
                "",
                "**Evidence:**",
                f"> {evidence['quote']}",
                "",
                f"**Page:** "
                f"{evidence['page']}",
                "",
            ]
        )

    lines.extend(
        [
            "## Conflicts",
            "",
        ]
    )

    conflicts = state.get(
        "conflicts",
        []
    )

    if not conflicts:

        lines.append(
            "No conflicts detected."
        )

    else:

        for index, conflict in enumerate(
            conflicts,
            start=1,
        ):

            lines.extend(
                [
                    f"### Conflict {index}",
                    "",
                    f"**Fact:** "
                    f"{conflict['fact_type']}",
                    "",
                ]
            )

            for value in conflict[
                "values"
            ]:

                evidence = value[
                    "evidence"
                ]

                lines.extend(
                    [
                        f"**Value:** "
                        f"{value['value']}",

                        f"**Source:** "
                        f"{value['filename']}",

                        f"**Evidence:** "
                        f"> {evidence['quote']}",

                        "",
                    ]
                )

    return {
        **state,
        "report": "\n".join(lines),
    }


def build_graph():

    graph = StateGraph(
        AgentState
    )

    graph.add_node(
        "ingest",
        ingest_documents,
    )

    graph.add_node(
        "extract",
        extract_document_facts,
    )

    graph.add_node(
        "normalize",
        normalize_facts,
    )

    graph.add_node(
        "detect_conflicts",
        detect_conflicts,
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
        "extract",
    )

    graph.add_edge(
        "extract",
        "normalize",
    )

    graph.add_edge(
        "normalize",
        "detect_conflicts",
    )

    graph.add_edge(
        "detect_conflicts",
        "report",
    )

    graph.add_edge(
        "report",
        END,
    )

    return graph.compile()