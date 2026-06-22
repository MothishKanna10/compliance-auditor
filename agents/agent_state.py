from __future__ import annotations

from typing import Literal, TypedDict


Severity = Literal["Low", "Medium", "High"]


class Evidence(TypedDict):
    source: str
    page: int
    content: str
    score: float


class AuditFinding(TypedDict):
    regulation: str
    issue: str
    severity: Severity
    evidence: str
    recommendation: str
    confidence: float


class AuditState(TypedDict):
    draft: str
    evidence: list[Evidence]
    findings: list[AuditFinding]
    final_answer: str