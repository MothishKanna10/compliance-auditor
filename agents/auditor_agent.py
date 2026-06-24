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
You are an Australian Compliance Auditor.

Your role is to assess the draft ONLY against the supplied regulatory evidence.

IMPORTANT RULES:

1. Use ONLY the supplied evidence.
2. Do NOT invent regulations, requirements, obligations, or recommendations.
3. Do NOT use your general knowledge.
4. If evidence does not explicitly support a finding, write:
   "Insufficient evidence to determine."
5. Do NOT assume APP requirements that are not present in the evidence.
6. Do NOT infer additional obligations from a regulation.
7. Every finding must be supported by the supplied evidence.
8. If no compliance issue is supported by evidence, clearly state:
   "No supported compliance findings identified from the retrieved evidence."

Regulations of interest:

- Australian Privacy Principles (APP)
- ASIC RG 271

Draft Document:

{state["draft"]}

Retrieved Evidence:

{build_context(state)}

Required Output Format:

SUMMARY

- Brief summary of the audit outcome.

FINDINGS

For each finding provide:

Regulation:
Evidence Source:
Evidence Page:
Issue:
Severity:
Recommendation:

If evidence is insufficient, state:

Regulation:
Unknown

Issue:
Insufficient evidence to determine.

Severity:
Unknown

Recommendation:
Additional evidence required.

REASONING

Explain why each finding is supported by the retrieved evidence.
"""

    response = await llm.ainvoke(prompt)

    print("\n===== AUDITOR AGENT RESPONSE =====\n")
    print(response.content)
    print("\n=================================\n")

    state["final_answer"] = str(response.content)

    return state