from langchain_chroma import Chroma
from app.config import settings
from app.embeddings import get_embeddings

def load_vector_store() -> Chroma:
    embeddings = get_embeddings()

    return Chroma(
        persist_directory=settings.chroma_dir,
        collection_name=settings.collection_name,
        embedding_function=embeddings,
    )


def search_rules(query: str, top_k: int = settings.top_k) -> None:
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