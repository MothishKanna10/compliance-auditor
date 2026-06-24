# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is an AI-powered compliance auditing tool that checks documents against Australian regulatory frameworks (APP Guidelines, ASIC RG 271). It uses a LangGraph multi-agent workflow backed by a local LLM (Ollama) and a ChromaDB vector store for retrieval-augmented generation.

## Running the App

The system has two services that run concurrently:

```bash
# 1. One-time: build the vector database from regulatory PDFs in data/
python -m app.ingestion

# 2. FastAPI backend (port 8000)
python -m uvicorn app.api:app --host 127.0.0.1 --port 8000 --reload

# 3. Streamlit frontend (port 8501) — in a separate terminal
streamlit run ui.py
```

Individual CLI tools for manual testing:
```bash
python run_phase1_agent.py         # Test the full LangGraph agent workflow
python -m app.compliance_checker   # Interactive document audit via CLI
python -m app.auditor              # Compliance Q&A with context retrieval
python -m app.retriever            # Semantic search testing against ChromaDB
```

There are no automated tests. Manual validation is done through the CLI entry points above.

## Architecture

### Data Flow

```
User document text
  → [retrieval_node] Semantic search in ChromaDB → top-5 regulatory chunks
  → [auditor_agent]  LLM analyzes document + evidence → findings
  → [reviewer_agent] LLM validates + assigns confidence (High/Medium/Low)
      ↳ If Low confidence and retry_count < 1: loop back to retrieval_node
  → [report_node]    Format final report
  → FastAPI /audit response → Streamlit UI
```

### Key Components

| Layer | File(s) | Role |
|---|---|---|
| Workflow orchestration | `agents/compliance_graph.py` | LangGraph `StateGraph` wiring the 4-node DAG |
| State schema | `agents/agent_state.py` | `TypedDict` shared across all nodes |
| Retrieval | `agents/retrieval_node.py` | Queries ChromaDB, populates `evidence` in state |
| Audit LLM call | `agents/auditor_agent.py` | Prompts LLM with document + evidence |
| Review LLM call | `agents/reviewer_agent.py` | Validates findings, sets `confidence` and retry logic |
| Report formatting | `agents/report_node.py` | Formats the final markdown report |
| API entry point | `app/api.py` | FastAPI `/audit` POST endpoint |
| Audit orchestration | `app/services/audit_service.py` | Invokes the LangGraph workflow |
| Vector DB setup | `app/ingestion.py` | PDF loading → chunking → embedding → ChromaDB |
| LLM initialization | `app/llm.py` | Configures Ollama or OpenAI based on `.env` |
| Embedding init | `app/embeddings.py` | HuggingFace `all-MiniLM-L6-v2` |
| Frontend | `ui.py` | Streamlit form that POSTs to the FastAPI backend |

### Configuration (`.env`)

- `LLM_PROVIDER=llama` — uses local Ollama; set to `openai` to use GPT-4o
- `LLM_MODEL=llama3.2:3b`
- `EMBEDDING_PROVIDER=huggingface`
- `CHUNK_SIZE=1000`, `CHUNK_OVERLAP=150`, `TOP_K=5`

Config is loaded via `app/config.py` using Pydantic `BaseSettings`.

### Vector Store

ChromaDB is persisted to `chroma_db/`. Re-run `python -m app.ingestion` whenever PDFs in `data/` change. The store is queried at runtime by `app/retriever.py`, which is called from `agents/retrieval_node.py`.

### Regulatory Scope

The regulatory documents in `data/` cover:
- **APP Guidelines** — Australian Privacy Principles (APP 1, 5, 6, 11)
- **ASIC RG 271** — Internal Dispute Resolution standards

## Current Progress

**Completed**
- PDF ingestion pipeline (PyPDF2 → chunking → ChromaDB)
- ChromaDB vector database with HuggingFace embeddings
- Retrieval workflow (semantic search, top-k evidence selection)
- LangGraph multi-agent workflow (4-node StateGraph)
- Reviewer agent with confidence scoring and retry logic
- FastAPI backend (`/audit` endpoint)
- Streamlit frontend

**Planned**
- PDF upload (file upload UI instead of raw text input)
- DOCX upload support
- Chat history / conversational audit interface
- Docker containerisation
- GitHub Actions CI/CD pipeline
- LangSmith tracing and observability
- DeepEval evaluation framework for agent quality
- Azure OpenAI as an alternative LLM provider
- Render deployment
