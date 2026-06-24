from fastapi import FastAPI

from app.schemas import AuditRequest, AuditResponse
from app.services.audit_service import run_audit


app = FastAPI(
    title="AI Compliance Auditor",
    description="Australian Privacy Principles (APP) and ASIC RG271 Compliance Auditor",
    version="1.0.0",
)


@app.get("/")
async def health_check() -> dict[str, str]:
    return {
        "status": "running",
    }


@app.post(
    "/audit",
    response_model=AuditResponse,
)
async def audit_document(
    request: AuditRequest,
) -> AuditResponse:
    result = await run_audit(
        request.document_text,
    )

    return AuditResponse(
        report=result["report"],
        confidence=result["confidence"],
    )