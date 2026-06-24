from __future__ import annotations

from langchain_chroma import Chroma

from agents.agent_state import AuditState, Evidence
from app.config import settings
from app.embeddings import get_embeddings


def get_vector_store() -> Chroma:
    embeddings = get_embeddings()

    return Chroma(
        collection_name=settings.collection_name,
        persist_directory=settings.chroma_dir,
        embedding_function=embeddings,
    )


def _draft_sentences(draft: str) -> list[str]:
    return [s.strip() for s in draft.splitlines() if s.strip()]


async def retrieve_rules_node(state: AuditState) -> AuditState:
    vector_store = get_vector_store()

    sentences = _draft_sentences(state["draft"])
    queries = sentences if sentences else [state["draft"]]

    seen: set[str] = set()
    evidence: list[Evidence] = []

    for query in queries:
        results = vector_store.similarity_search_with_score(
            query=query,
            k=settings.top_k,
        )

        for document, score in results:
            if document.page_content in seen:
                continue

            seen.add(document.page_content)
            metadata = document.metadata

            evidence.append(
                {
                    "source": str(metadata.get("source", "unknown")),
                    "page": int(metadata.get("page", 0)),
                    "content": document.page_content,
                    "score": float(score),
                }
            )

    state["evidence"] = evidence

    print("\n========== RETRIEVAL NODE ==========")
    print(f"Retrieved {len(evidence)} chunks\n")

    for index, item in enumerate(evidence, start=1):
        print(f"----- Chunk {index} -----")
        print(f"Source : {item['source']}")
        print(f"Page   : {item['page']}")
        print(f"Score  : {item['score']:.4f}")

        print("\nContent:")
        print(item["content"][:1000])

        print("\n" + "-" * 60 + "\n")

    print("====================================\n")

    return state