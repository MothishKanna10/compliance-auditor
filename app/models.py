from __future__ import annotations

from typing import Literal, TypedDict


Severity = Literal[
    "Low",
    "Medium",
    "High",
]


class EvidenceItem(
    TypedDict,
    total=False,
):
    source: str
    page: str
    score: str


class AuditFinding(
    TypedDict,
):
    rule: str
    severity: Severity
    issue: str
    recommendation: str
    evidence: list[EvidenceItem]


class AuditResult(
    TypedDict,
):
    summary: str
    findings: list[AuditFinding]