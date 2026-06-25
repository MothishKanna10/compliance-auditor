# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

An AI-powered compliance auditing tool that checks documents against Australian regulatory frameworks (APP Guidelines, ASIC RG 271). Uses a LangGraph multi-agent workflow, OpenAI GPT-4o-mini for LLM calls, OpenAI text-embedding-3-small for embeddings, and ChromaDB for vector storage.

## Running the App

Two services must run concurrently:

```bash
# One-time: build the vector database from regulatory PDFs in data/
python -m app.ingestion

# Terminal 1 — FastAPI backend (port 8000)
python -m uvicorn app.api:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2 — Streamlit frontend (port 8501)
streamlit run ui.py
```

Re-run ingestion only when PDFs in `data/` change. ChromaDB persists to `chroma_db/`.

## Architecture

### Data Flow

```
User document (PDF / DOCX / TXT / pasted text)
  → [retrieval_node] Query rewriting → per-sentence ChromaDB search → top-2 chunks per sentence
  → [auditor_agent]  LLM analyses document + evidence → structured findings
  → [reviewer_agent] LLM validates findings → confidence (High/Medium/Low)
      ↳ If Low confidence and retry_count < 1: loop back with reviewer feedback
  → [report_node]    Format final report (AUDIT FINDINGS + REVIEWER ASSESSMENT)
  → FastAPI /audit or /audit/file response → Streamlit UI
  → [/chat endpoint] Follow-up Q&A about the report (session-only, no persistence)
```

### Key Components

| Layer | File(s) | Role |
|---|---|---|
| Workflow orchestration | `agents/compliance_graph.py` | LangGraph `StateGraph` — 4-node DAG |
| State schema | `agents/agent_state.py` | `AuditState` TypedDict shared across all nodes |
| Retrieval | `agents/retrieval_node.py` | Sentence splitting, query rewriting, per-sentence ChromaDB search |
| Audit LLM call | `agents/auditor_agent.py` | Prompts LLM with numbered sentences + evidence |
| Review LLM call | `agents/reviewer_agent.py` | Validates findings, sets confidence, stores reviewer_notes |
| Report formatting | `agents/report_node.py` | Formats two-section report |
| API entry point | `app/api.py` | FastAPI `/audit`, `/audit/file`, `/chat` endpoints |
| Audit orchestration | `app/services/audit_service.py` | Invokes the LangGraph workflow |
| Chat service | `app/services/chat_service.py` | LLM Q&A using audit report as context |
| Vector DB setup | `app/ingestion.py` | PDF loading → 150-char filter → chunking → ChromaDB |
| LLM initialisation | `app/llm.py` | Returns ChatOpenAI or ChatOllama based on LLM_PROVIDER |
| Embedding init | `app/embeddings.py` | Returns OpenAIEmbeddings or HuggingFaceEmbeddings |
| Document parsing | `app/document_parser.py` | Extracts text from PDF, DOCX, TXT uploads |
| Frontend | `ui.py` | Streamlit UI — upload/paste tabs, report display, chat interface |

### Configuration (`.env`)

```
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=<your key>
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
CHUNK_SIZE=1000
CHUNK_OVERLAP=150
TOP_K=5
CHROMA_PERSIST_DIR=chroma_db
CHROMA_COLLECTION_NAME=compliance_rules
DATA_DIR=data
```

### Retrieval Pipeline

1. **Sentence splitting** — splits any document format (paragraphs, bullets, numbered sections) into individual sentences. Capped at 40 sentences.
2. **Query rewriting** — one LLM call rewrites all sentences into legal search queries (e.g. "We may share with third parties" → "use or disclose personal information to third parties APP 6"). Fixes vocabulary mismatch between plain English and legal text.
3. **Per-sentence search** — top-2 ChromaDB chunks per sentence (not global top-k), so every sentence gets relevant evidence from the right chapter.
4. **Retry with feedback** — if reviewer assigns Low confidence, loops back with reviewer notes to generate more targeted queries.

### Regulatory Scope

PDFs in `data/` cover all 13 APP chapters (individual files per chapter) + ASIC RG 271:
- **APP 1** — Open and transparent management
- **APP 3** — Collection of solicited personal information
- **APP 5** — Notification of collection
- **APP 6** — Use or disclosure of personal information
- **APP 11** — Security of personal information
- **APP 12** — Access to personal information
- **APP 13** — Correction of personal information
- *(APP 2, 4, 7, 8, 9, 10 also ingested)*
- **ASIC RG 271** — Internal Dispute Resolution

## Current Progress

**Completed**
- PDF ingestion pipeline with 150-char chunk filter
- Individual APP chapter PDFs (APP 1–13) + ASIC RG 271
- OpenAI embeddings (text-embedding-3-small)
- Per-sentence retrieval with query rewriting
- LangGraph 4-node multi-agent workflow
- Reviewer agent with confidence scoring and retry with feedback
- FastAPI backend (`/audit`, `/audit/file`, `/chat` endpoints)
- Streamlit frontend with file upload, paste text, report display, chat interface
- Confidence badge (colour-coded), download report button

**Planned**
- Docker containerisation
- GitHub Actions CI/CD pipeline
- LangSmith tracing and observability
- DeepEval evaluation framework for agent quality
- Azure OpenAI as an alternative LLM provider
- Render deployment
