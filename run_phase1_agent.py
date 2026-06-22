from __future__ import annotations

import asyncio

from agents.agent_state import AuditState
from agents.compliance_graph import build_phase1_compliance_graph


async def main() -> None:
    draft = """
    We aim to resolve customer complaints within 45 business days.

    Customer personal information may be stored in third-party systems.

    Security controls will be applied where practical.
    """

    initial_state: AuditState = {
        "draft": draft,
        "evidence": [],
        "findings": [],
        "final_answer": "",
    }

    graph = build_phase1_compliance_graph()

    result = await graph.ainvoke(initial_state)

    print("\n========== FINAL AUDIT ==========\n")

    print(result["final_answer"])


if __name__ == "__main__":
    asyncio.run(main())