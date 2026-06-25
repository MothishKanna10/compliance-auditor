from __future__ import annotations

from typing import TypedDict


class Evidence(TypedDict):
    source: str
    page: int
    content: str
    score: float


class AuditState(TypedDict):
    draft: str
    evidence: list[Evidence]
    final_answer: str
    reviewer_notes: str
    confidence: str
    retry_count: int