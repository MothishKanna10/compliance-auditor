from __future__ import annotations

from langchain_ollama import ChatOllama

from agents.agent_state import AuditState
from app.config import settings


def build_context(state: AuditState) -> str:
    return "\n\n".join(
        f"Source: {item['source']} | Page: {item['page']}\n{item['content']}"
        for item in state["evidence"]
    )


async def auditor_agent_node(state: AuditState) -> AuditState:
    llm = ChatOllama(
        model=settings.llm_model,
        temperature=0,
    )

    prompt = f"""
You are an Australian compliance auditor.

Your task is to audit the draft against:

1. Australian Privacy Principles (APP)
2. ASIC RG 271

Instructions:
- Use only the supplied evidence.
- Identify any compliance violations.
- Mention the relevant regulation.
- Assess severity (Low, Medium, High).
- Provide recommendations.
- Explain your reasoning.

Draft:

{state["draft"]}

Evidence:

{build_context(state)}
"""

    response = await llm.ainvoke(prompt)

    print("\n===== AUDITOR AGENT RESPONSE =====\n")
    print(response.content)
    print("\n=================================\n")

    state["final_answer"] = str(response.content)

    return state