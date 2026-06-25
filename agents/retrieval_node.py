from __future__ import annotations

import re

from langchain_chroma import Chroma

from agents.agent_state import AuditState, Evidence
from app.config import settings
from app.embeddings import get_embeddings
from app.llm import get_llm

_MAX_SENTENCES = 40


def get_vector_store() -> Chroma:
    embeddings = get_embeddings()

    return Chroma(
        collection_name=settings.collection_name,
        persist_directory=settings.chroma_dir,
        embedding_function=embeddings,
    )


def _draft_sentences(draft: str) -> list[str]:
    sentences = []

    for line in draft.splitlines():
        line = line.strip()
        if not line:
            continue

        line = re.sub(r"^(\d+[\.\)]|[•\-\*]|Section\s+\d+[:\.]?)\s*", "", line, flags=re.IGNORECASE)
        line = line.strip()
        if not line:
            continue

        parts = re.split(r"(?<=[.!?])\s+", line)
        for part in parts:
            part = part.strip()
            if len(part) > 10:
                sentences.append(part)

    return sentences[:_MAX_SENTENCES]


async def _rewrite_queries(sentences: list[str]) -> list[str]:
    """
    Rewrites plain-English policy sentences into precise legal search queries.
    One LLM call for all sentences — maps "share" → "disclose", etc.
    """
    llm = get_llm()

    numbered = "\n".join(f"{i + 1}. {s}" for i, s in enumerate(sentences))

    prompt = f"""You are a legal search query optimizer for Australian Privacy Principles (APP).

Convert each policy sentence into a precise regulatory search query using legal terminology.
Use terms like: "use or disclose", "secondary purpose", "APP 6", "collection notice APP 5",
"security obligation APP 11", "access to personal information APP 12", etc.

Output ONLY the rewritten queries, one per line, numbered the same way. No explanation.

Policy sentences:
{numbered}

Rewritten search queries:"""

    response = await llm.ainvoke(prompt)

    lines = [l.strip() for l in response.content.strip().splitlines() if l.strip()]
    queries = []
    for line in lines:
        cleaned = re.sub(r"^\d+[\.\)]\s*", "", line).strip()
        if cleaned:
            queries.append(cleaned)

    if len(queries) != len(sentences):
        return sentences

    return queries


async def retrieve_rules_node(state: AuditState) -> AuditState:
    vector_store = get_vector_store()

    sentences = _draft_sentences(state["draft"])
    if not sentences:
        sentences = [state["draft"]]

    print("\n========== QUERY REWRITING ==========")
    rewritten = await _rewrite_queries(sentences)
    for orig, rewr in zip(sentences, rewritten):
        print(f"  Original : {orig}")
        print(f"  Rewritten: {rewr}")
        print()

    seen: set[str] = set()
    evidence: list[Evidence] = []

    per_sentence_k = 2

    for rewritten_query in rewritten:
        results = vector_store.similarity_search_with_score(
            query=rewritten_query,
            k=per_sentence_k + 2,
        )

        added = 0
        for document, score in results:
            if added >= per_sentence_k:
                break
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
            added += 1

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
