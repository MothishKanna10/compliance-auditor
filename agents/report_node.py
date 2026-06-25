from __future__ import annotations

from agents.agent_state import AuditState


async def report_node(state: AuditState) -> AuditState:
    report = f"""COMPLIANCE AUDIT REPORT
{'=' * 40}

AUDIT FINDINGS
{'-' * 40}
{state['final_answer']}

REVIEWER ASSESSMENT
{'-' * 40}
{state.get('reviewer_notes', '')}
"""

    state["final_answer"] = report

    return state