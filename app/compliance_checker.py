from __future__ import annotations

from ollama import chat

from models import EvidenceItem
from retriever import load_vector_store


def retrieve_relevant_rules(
    draft_text: str,
    top_k: int = 10,
) -> tuple[str, list[EvidenceItem]]:
    vector_store = load_vector_store()

    results = vector_store.similarity_search_with_score(
        query=draft_text,
        k=top_k,
    )

    context_parts: list[str] = []
    evidence: list[EvidenceItem] = []

    for document, score in results:
        context_parts.append(
            document.page_content
        )

        evidence.append(
            {
                "source": str(
                    document.metadata.get(
                        "source",
                        "Unknown Source",
                    )
                ),
                "page": str(
                    document.metadata.get(
                        "page",
                        "Unknown",
                    )
                ),
                "score": f"{score:.4f}",
            }
        )

    return "\n\n".join(context_parts), evidence


def build_audit_prompt(
    draft_text: str,
    regulatory_context: str,
) -> str:
    return f"""
You are an Australian Compliance Auditor.

Your task is to audit the draft business document
against the supplied regulatory context.

Use ONLY the supplied regulatory context.

Do NOT invent laws,
regulations,
penalties,
or obligations.

Focus on:

- Australian Privacy Principles
- APP 1
- APP 5
- APP 6
- APP 11
- Privacy Collection Notices
- Disclosure of Personal Information
- Security of Personal Information
- Complaint Handling
- ASIC RG 271

Return the answer in the following format:

SUMMARY:
<short summary>

FINDINGS:

1. Rule:
Severity:
Issue:
Recommendation:

2. Rule:
Severity:
Issue:
Recommendation:

If no issues are identified, say:

"No clear compliance issue found from the supplied context."

REGULATORY CONTEXT:
{regulatory_context}

DRAFT DOCUMENT:
{draft_text}
"""


def format_evidence(
    evidence: list[EvidenceItem],
) -> str:
    if not evidence:
        return "No evidence returned."

    seen: set[tuple[str, str]] = set()

    lines: list[str] = []

    for item in evidence:
        key = (
            item["source"],
            item["page"],
        )

        if key in seen:
            continue

        seen.add(key)

        lines.append(
            f"- Source: {item['source']} "
            f"| Page: {item['page']} "
            f"| Similarity Score: {item.get('score', 'N/A')}"
        )

    return "\n".join(lines)


def audit_draft_document(
    draft_text: str,
) -> str:
    regulatory_context, evidence = retrieve_relevant_rules(
        draft_text=draft_text,
        top_k=10,
    )

    if not regulatory_context:
        return (
            "No relevant regulatory context "
            "found in the vector database."
        )

    prompt = build_audit_prompt(
        draft_text=draft_text,
        regulatory_context=regulatory_context,
    )

    response = chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    answer = str(
        response["message"]["content"]
    )

    evidence_text = format_evidence(
        evidence
    )

    return (
        f"{answer}\n\n"
        f"EVIDENCE USED:\n"
        f"{evidence_text}"
    )


def main() -> None:
    print(
        "Paste a draft business/privacy document below."
    )
    print(
        "Type END on a new line when finished.\n"
    )

    lines: list[str] = []

    while True:
        line = input()

        if line.strip().upper() == "END":
            break

        lines.append(line)

    draft_text = "\n".join(lines).strip()

    if not draft_text:
        print(
            "Draft document cannot be empty."
        )
        return

    result = audit_draft_document(
        draft_text=draft_text
    )

    print("\nAUDIT RESULT")
    print("=" * 80)
    print(result)


if __name__ == "__main__":
    main()