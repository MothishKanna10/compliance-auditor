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

    draft_sentences = [
        s.strip()
        for s in state["draft"].splitlines()
        if s.strip()
    ]
    numbered_draft = "\n".join(
        f"[{i+1}] {s}" for i, s in enumerate(draft_sentences)
    )

    prompt = f"""
You are an Australian Compliance Auditor.

The draft document contains EXACTLY these sentences — nothing else:

{numbered_draft}

Retrieved Regulatory Evidence:
{build_context(state)}

Your task: for each numbered sentence above, check whether it breaches an obligation stated in the retrieved evidence.

STRICT RULES:
1. You may ONLY reference sentences listed above as [1], [2], [3], etc.
2. Do NOT invent, paraphrase, or add sentences that are not in the numbered list.
3. A finding is valid only if BOTH are true:
   a. The numbered sentence makes a claim that falls short of the regulation.
   b. The retrieved evidence explicitly states that obligation.
4. Do NOT use general knowledge. Do NOT invent regulations.
5. Omit any finding not supported by both the draft and the evidence.
6. If no breach is found, output only: "No supported compliance findings identified."

FINDINGS

For each valid breach only:

Draft Sentence: [<number>] <exact text from the numbered list above>
Regulation: <regulation name and number>
Evidence Source: <source>
Evidence Page: <page>
Issue: <why this sentence breaches or falls short of the regulation>
Severity: <High | Medium | Low>
Recommendation: <specific corrective wording>
Reasoning: <quote the evidence passage that supports this>

SUMMARY

One paragraph summarising all findings, or state that none were found.
"""

    response = await llm.ainvoke(prompt)

    print("\n===== AUDITOR AGENT RESPONSE =====\n")
    print(response.content)
    print("\n=================================\n")

    state["final_answer"] = str(response.content)

    return state