from __future__ import annotations

from agents.agent_state import AuditState


async def report_node(state: AuditState) -> AuditState:
    report = f"""
========== FINAL REPORT ==========

Confidence: {state['confidence']}

{state['final_answer']}
"""

    state["final_answer"] = report

    return state