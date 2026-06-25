from fastapi import FastAPI, File, HTTPException, UploadFile

from app.document_parser import extract_text_from_uploaded_file
from app.schemas import AuditRequest, AuditResponse, ChatRequest, ChatResponse
from app.services.audit_service import run_audit
from app.services.chat_service import run_chat


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


@app.post(
    "/audit/file",
    response_model=AuditResponse,
)
async def audit_file(
    file: UploadFile = File(...),
) -> AuditResponse:
    file_bytes = await file.read()

    try:
        document_text = extract_text_from_uploaded_file(
            file.filename or "",
            file_bytes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if not document_text.strip():
        raise HTTPException(status_code=422, detail="File appears to be empty or contains no extractable text.")

    result = await run_audit(document_text)

    return AuditResponse(
        report=result["report"],
        confidence=result["confidence"],
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    answer = await run_chat(
        report=request.report,
        messages=request.messages,
        question=request.question,
    )
    return ChatResponse(answer=answer)