from pydantic import BaseModel


class AuditRequest(BaseModel):
    document_text: str


class AuditResponse(BaseModel):
    report: str
    confidence: str