from pydantic import BaseModel


class AuditRequest(BaseModel):
    document_text: str


class AuditResponse(BaseModel):
    report: str
    confidence: str


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    report: str
    messages: list[ChatMessage]
    question: str


class ChatResponse(BaseModel):
    answer: str