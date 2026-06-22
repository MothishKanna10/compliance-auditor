from __future__ import annotations
from app.config import settings
from langchain_chroma import Chroma
from app.embeddings import get_embeddings
from agents.agent_state import AuditState, Evidence


def get_vector_store() -> Chroma:
    embeddings = get_embeddings()

    return Chroma(
        collection_name=settings.collection_name,
        persist_directory=settings.chroma_dir,
        embedding_function=embeddings,
    )


async def retrieve_rules_node(state: AuditState) -> AuditState:
    vector_store = get_vector_store()

    top_k = settings.top_k

    results = vector_store.similarity_search_with_score(
        query=state["draft"],
        k=top_k,
    )

    evidence: list[Evidence] = []

    for document, score in results:
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

    return state