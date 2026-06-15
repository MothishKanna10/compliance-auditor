from ollama import chat

from retriever import load_vector_store


def retrieve_context(
    query: str,
    top_k: int = 5,
) -> tuple[str, list[dict[str, str]]]:
    vector_store = load_vector_store()

    results = vector_store.similarity_search(
        query=query,
        k=top_k,
    )

    context_parts: list[str] = []
    evidence: list[dict[str, str]] = []

    for document in results:
        context_parts.append(document.page_content)

        evidence.append(
            {
                "source": document.metadata.get(
                    "source",
                    "Unknown Source",
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
    prompt = f"""
You are an Australian Compliance Auditor.

Answer ONLY using the supplied context.

If the answer is not present in the context,
state that clearly.

Context:
{context}

Question:
{query}
"""

    response = chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response["message"]["content"]


def main() -> None:
    query = input(
        "Ask a compliance question: "
    ).strip()

    if not query:
        print("Query cannot be empty.")
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