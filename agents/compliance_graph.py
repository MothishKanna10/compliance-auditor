from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from agents.agent_state import AuditState
from agents.auditor_agent import auditor_agent_node
from agents.retrieval_node import retrieve_rules_node


def build_phase1_compliance_graph():
    graph = StateGraph(AuditState)

    graph.add_node(
        "retrieve_rules",
        retrieve_rules_node,
    )

    graph.add_node(
        "audit_draft",
        auditor_agent_node,
    )

    graph.add_edge(
        START,
        "retrieve_rules",
    )

    graph.add_edge(
        "retrieve_rules",
        "audit_draft",
    )

    graph.add_edge(
        "audit_draft",
        END,
    )

    return graph.compile()