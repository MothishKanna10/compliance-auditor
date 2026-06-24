from __future__ import annotations

import asyncio

from agents.agent_state import AuditState
from agents.compliance_graph import build_phase3_graph


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
        "confidence": "",
        "retry_count": 0,
    }



if __name__ == "__main__":
    asyncio.run(main())