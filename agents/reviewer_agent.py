from __future__ import annotations

from agents.agent_state import AuditState
from app.config import settings
from app.llm import get_llm


def build_evidence_context(state: AuditState) -> str:
    return "\n\n".join(
        f"Source: {item['source']} | Page: {item['page']}\n{item['content']}"
        for item in state["evidence"]
    )


async def reviewer_agent_node(state: AuditState) -> AuditState:
    llm = get_llm()

    prompt = f"""
You are a compliance review agent.

Your job is to review the audit answer against the retrieved evidence.

Retrieved Evidence:

{build_evidence_context(state)}

Audit Answer:

{state["final_answer"]}

Tasks:

1. Determine whether the answer is supported by the evidence.
2. Identify possible hallucinations or unsupported claims.
3. Assign a confidence level:
   - High
   - Medium
   - Low

Give a short explanation.

Format:

Confidence: <High|Medium|Low>

Reason:
<short explanation>
"""

    response = await llm.ainvoke(prompt)

    review = str(response.content)

    print("\n===== REVIEWER AGENT =====\n")
    print(review)
    print("\n==========================\n")

    confidence = "Medium"

    review_lower = review.lower()

    if "confidence: high" in review_lower:
        confidence = "High"

    elif "confidence: low" in review_lower:
        confidence = "Low"

    state["confidence"] = confidence
    state["reviewer_notes"] = review

    return state