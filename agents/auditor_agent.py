from __future__ import annotations

from agents.agent_state import AuditState
from app.config import settings
from app.llm import get_llm


def build_context(state: AuditState) -> str:
    return "\n\n".join(
        f"Source: {item['source']} | Page: {item['page']}\n{item['content']}"
        for item in state["evidence"]
    )


async def auditor_agent_node(state: AuditState) -> AuditState:
    llm = get_llm()

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

Your task: for each numbered sentence, identify compliance issues against the retrieved evidence.

STRICT RULES:
1. You may ONLY reference sentences listed above as [1], [2], [3], etc.
2. Do NOT invent, paraphrase, or add sentences that are not in the numbered list.
3. A finding is valid if the retrieved evidence states an obligation AND the numbered sentence:
   a. Explicitly contradicts or falls short of that obligation, OR
   b. States or implies a practice (e.g. sharing, storing, collecting data) WITHOUT including
      the conditions, consent, or safeguards that the obligation requires, OR
   c. Uses vague language (e.g. "business purposes", "may share", "for our purposes") where
      the regulation requires specificity, stated purpose, or explicit conditions.
4. Do NOT use general knowledge. Do NOT invent regulations.
5. Only raise a finding if the evidence passage directly supports it — quote it exactly.
6. If no breach is found, output only: "No supported compliance findings identified."

EXAMPLES of valid findings:
- Sentence says "We may share data with third parties" + evidence says disclosure requires consent
  or a listed exception → VALID (sharing implied without required conditions)
- Sentence says "We store data for business purposes" + evidence says entity must take reasonable
  steps to protect personal information → VALID (vague purpose, no security commitment stated)
- Sentence says "Contact us with questions" + evidence says entity must give access on request
  → VALID (access right not explicitly stated as required)

FINDINGS

For each valid finding only:

Draft Sentence: [<number>] <exact text from the numbered list above>
Regulation: <regulation name and number>
Evidence Source: <source file>
Evidence Page: <page number>
Issue: <why this sentence breaches or is insufficient under the regulation>
Severity: <High | Medium | Low>
Recommendation: <specific corrective wording to fix the sentence>
Reasoning: <exact quote from the evidence that supports this finding>

SUMMARY

One paragraph summarising all findings, or state that none were found.
"""

    response = await llm.ainvoke(prompt)

    print("\n===== AUDITOR AGENT RESPONSE =====\n")
    print(response.content)
    print("\n=================================\n")

    state["final_answer"] = str(response.content)

    return state