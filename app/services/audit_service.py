from agents.agent_state import AuditState
from agents.compliance_graph import build_phase3_graph


async def run_audit(
    document_text: str,
) -> dict[str, str]:

    initial_state: AuditState = {
        "draft": document_text,
        "evidence": [],
        "final_answer": "",
        "reviewer_notes": "",
        "confidence": "",
        "retry_count": 0,
    }

    graph = build_phase3_graph()

    result = await graph.ainvoke(
        initial_state,
    )

    return {
        "report": result["final_answer"],
        "confidence": result["confidence"],
    }