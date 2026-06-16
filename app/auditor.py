from __future__ import annotations

from typing import TypedDict

from app.llm import get_llm
from app.retriever import load_vector_store


class EvidenceItem(TypedDict):
    source: str
    page: str


def retrieve_context(
    query: str,
    top_k: int = 5,
) -> tuple[str, list[EvidenceItem]]:
    vector_store = load_vector_store()

    results = vector_store.similarity_search(
        query=query,
        k=top_k,
    )

    context_parts: list[str] = []
    evidence: list[EvidenceItem] = []

    for document in results:
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
            }
        )

    return "\n\n".join(context_parts), evidence


def generate_answer(
    query: str,
    context: str,
) -> str:
    llm = get_llm()

    prompt = f"""
You are an Australian Compliance Auditor.

Answer the question using ONLY the supplied regulatory context.

If the context contains a partial answer, explain only what is supported by the context.
Do not say the answer is missing if the context includes relevant APP wording.

Use this structure:

ANSWER:
<clear answer>

SOURCE BASIS:
<briefly mention which APP/RG rule from the context supports the answer>

Context:
{context}

Question:
{query}
"""

    response = llm.invoke(prompt)

    return str(response.content)

def main() -> None:
    query = input(
        "Ask a compliance question: "
    ).strip()

    if not query:
        print(
            "Query cannot be empty."
        )
        return

    context, evidence = retrieve_context(
        query=query,
        top_k=5,
    )

    answer = generate_answer(
        query=query,
        context=context,
    )

    print("\nAnswer:")
    print("-" * 80)
    print(answer)

    print("\nEvidence Used:")
    print("-" * 80)

    seen: set[tuple[str, str]] = set()

    for item in evidence:
        key = (
            item["source"],
            item["page"],
        )

        if key not in seen:
            seen.add(key)

            print(
                f"Source: {item['source']} | "
                f"Page: {item['page']}"
            )


if __name__ == "__main__":
    main()