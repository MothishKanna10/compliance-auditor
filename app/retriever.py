from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma


def create_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


def load_vector_store() -> Chroma:
    embeddings = create_embeddings()

    return Chroma(
        persist_directory="chroma_db",
        collection_name="compliance_rules",
        embedding_function=embeddings,
    )


def search_rules(query: str, top_k: int = 5) -> None:
    vector_store = load_vector_store()

    results = vector_store.similarity_search_with_score(
        query=query,
        k=top_k,
    )

    print("\nSearch Query:")
    print(query)

    print("\nTop Relevant Regulatory Chunks:")

    for index, (document, score) in enumerate(results, start=1):
        source = document.metadata.get("source", "Unknown source")
        page = document.metadata.get("page", "Unknown page")

        print("\n" + "=" * 80)
        print(f"Result {index}")
        print(f"Source: {source}")
        print(f"Page: {page}")
        print(f"Similarity Score: {score}")
        print("-" * 80)
        print(document.page_content[:1200])


def main() -> None:
    query = input("Ask a compliance question: ").strip()

    if not query:
        print("Query cannot be empty.")
        return

    search_rules(query=query, top_k=5)


if __name__ == "__main__":
    main()