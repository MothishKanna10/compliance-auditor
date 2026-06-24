from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from agents.agent_state import AuditState
from agents.auditor_agent import auditor_agent_node
from agents.report_node import report_node
from agents.retrieval_node import retrieve_rules_node
from agents.reviewer_agent import reviewer_agent_node


def should_retry(state: AuditState) -> str:
    if state["confidence"] == "Low" and state["retry_count"] < 1:
        state["retry_count"] += 1
        return "retrieve"

    return "report"


def build_phase3_graph():
    graph = StateGraph(AuditState)

    graph.add_node(
        "retrieve",
        retrieve_rules_node,
    )

    graph.add_node(
        "audit",
        auditor_agent_node,
    )

    graph.add_node(
        "review",
        reviewer_agent_node,
    )

    graph.add_node(
        "report",
        report_node,
    )

    graph.add_edge(
        START,
        "retrieve",
    )

    graph.add_edge(
        "retrieve",
        "audit",
    )

    graph.add_edge(
        "audit",
        "review",
    )

    graph.add_conditional_edges(
        "review",
        should_retry,
        {
            "retrieve": "retrieve",
            "report": "report",
        },
    )

    graph.add_edge(
        "report",
        END,
    )

    return graph.compile()