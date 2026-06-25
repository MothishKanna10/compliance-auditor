# ⚖️ AI Compliance Auditor

An AI-powered compliance auditing system that reviews business documents against Australian regulatory frameworks using a multi-agent LangGraph workflow, retrieval-augmented generation (RAG), and OpenAI GPT-4o-mini.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![LangGraph](https://img.shields.io/badge/LangGraph-multi--agent-orange)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-green?logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-frontend-red?logo=streamlit)
![ChromaDB](https://img.shields.io/badge/ChromaDB-vector--store-purple)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-black?logo=openai)

---

## Overview

This tool audits privacy policies and compliance documents against:

- **Australian Privacy Principles (APP 1–13)** — OAIC guidelines covering collection, use, disclosure, security, and access to personal information
- **ASIC RG 271** — Internal Dispute Resolution standards

Upload a PDF, DOCX, or TXT document. The system retrieves the relevant regulatory evidence, identifies violations, assigns severity, and provides specific recommendations — then lets you chat with the report.

---

## Architecture

```
User Document (PDF / DOCX / TXT / pasted text)
        │
        ▼
┌─────────────────────────────────────────────────┐
│              retrieval_node                     │
│  1. Split into sentences (any format)           │
│  2. Rewrite queries into legal terminology      │
│  3. Per-sentence ChromaDB search (top-2 each)   │
└─────────────────┬───────────────────────────────┘
                  │  evidence (regulatory chunks)
                  ▼
┌─────────────────────────────────────────────────┐
│              auditor_agent                      │
│  GPT-4o-mini analyses document vs evidence      │
│  Outputs: findings, severity, recommendations   │
└─────────────────┬───────────────────────────────┘
                  │  findings
                  ▼
┌─────────────────────────────────────────────────┐
│              reviewer_agent                     │
│  Validates findings against evidence            │
│  Assigns confidence: High / Medium / Low        │
│  Low confidence → retry with feedback           │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│              report_node                        │
│  Formats: AUDIT FINDINGS + REVIEWER ASSESSMENT  │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
        FastAPI → Streamlit UI
        (+ /chat endpoint for follow-up Q&A)
```

---

## Features

- **Multi-agent workflow** — LangGraph 4-node StateGraph: retrieval → audit → review → report
- **Query rewriting** — LLM rewrites plain-English sentences into legal terminology before searching (e.g. "We may share data" → "use or disclose personal information APP 6 obligation")
- **Per-sentence retrieval** — each sentence gets its own top-2 regulatory chunks, so no chapter dominates
- **Intelligent retry** — low-confidence results loop back with reviewer feedback for better queries
- **Any document format** — handles paragraphs, bullet points, numbered sections, PDFs, DOCX
- **Evidence-grounded findings** — every finding includes regulation reference, evidence quote, severity, and recommendation
- **Confidence scoring** — reviewer validates auditor output and assigns High / Medium / Low
- **Interactive chat** — ask follow-up questions about the report in a chat interface
- **Download report** — export audit results as a text file

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| LLM | OpenAI GPT-4o-mini |
| Embeddings | OpenAI text-embedding-3-small |
| Agent Framework | LangGraph + LangChain |
| Vector Database | ChromaDB |
| Backend | FastAPI + Pydantic |
| Frontend | Streamlit |
| Observability | LangSmith *(planned)* |
| Evaluation | DeepEval *(planned)* |
| Deployment | Docker + Render *(planned)* |

---

## Getting Started

### Prerequisites

- Python 3.11+
- OpenAI API key ([platform.openai.com](https://platform.openai.com))

### Installation

```bash
# Clone the repository
git clone https://github.com/MothishKanna10/compliance-auditor.git
cd compliance-auditor

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=your-api-key-here

EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small

CHROMA_PERSIST_DIR=chroma_db
CHROMA_COLLECTION_NAME=compliance_rules
DATA_DIR=data
CHUNK_SIZE=1000
CHUNK_OVERLAP=150
TOP_K=5
```

### Build the Vector Database

Run once — or re-run whenever PDFs in `data/` change:

```bash
python -m app.ingestion
```

### Run the Application

Open two terminals:

```bash
# Terminal 1 — FastAPI backend (port 8000)
python -m uvicorn app.api:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2 — Streamlit frontend (port 8501)
streamlit run ui.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Usage

1. **Upload** a PDF, DOCX, or TXT policy document — or paste text directly
2. Click **Run Audit**
3. Review the findings — each includes regulation, severity, and recommendation
4. **Chat** with the report — ask follow-up questions like:
   - *"Why is finding 2 High severity?"*
   - *"What does APP 6 require?"*
   - *"How do I fix sentence 3?"*
5. **Download** the report as a text file

---

## Project Structure

```
compliance-auditor/
├── agents/
│   ├── agent_state.py          # AuditState TypedDict
│   ├── compliance_graph.py     # LangGraph StateGraph wiring
│   ├── retrieval_node.py       # Sentence splitting, query rewriting, ChromaDB search
│   ├── auditor_agent.py        # Audit LLM call
│   ├── reviewer_agent.py       # Review + confidence scoring
│   └── report_node.py          # Report formatting
├── app/
│   ├── api.py                  # FastAPI endpoints (/audit, /audit/file, /chat)
│   ├── config.py               # Settings from .env
│   ├── document_parser.py      # PDF / DOCX / TXT text extraction
│   ├── embeddings.py           # OpenAI or HuggingFace embeddings
│   ├── ingestion.py            # PDF → chunks → ChromaDB
│   ├── llm.py                  # OpenAI or Ollama LLM provider
│   ├── schemas.py              # Pydantic request/response models
│   └── services/
│       ├── audit_service.py    # Invokes LangGraph workflow
│       └── chat_service.py     # Chat Q&A using report as context
├── data/                       # Regulatory PDFs (APP 1–13, ASIC RG 271)
├── chroma_db/                  # Persisted ChromaDB vector store
├── ui.py                       # Streamlit frontend
├── .env                        # Environment variables (not committed)
├── CLAUDE.md                   # Claude Code guidance
└── session-notes.md            # Development log
```

---

## Example Output

```
COMPLIANCE AUDIT REPORT
========================================

AUDIT FINDINGS
----------------------------------------
Draft Sentence: [2] We may share this information with third parties.
Regulation: APP 6 — Use or disclosure of personal information
Severity: High
Issue: Implies sharing without specifying required conditions or consent.
Recommendation: "We will only share this information with third parties when
we have obtained your consent or as permitted by law under APP 6."
Reasoning: "An APP entity may disclose personal information...
without relying on an exception in APP 6.2."

Draft Sentence: [3] We store customer information for business purposes.
Regulation: APP 11 — Security of personal information
Severity: Medium
Issue: Vague purpose with no security commitment stated.
Recommendation: "We store customer information securely and only as long as
necessary for specific business purposes."

REVIEWER ASSESSMENT
----------------------------------------
Confidence: High
All findings are well-supported by the retrieved evidence...
```

---

## Regulatory Coverage

| Regulation | Scope |
|---|---|
| APP 1 | Privacy policy — transparency and openness |
| APP 3 | Collection of solicited personal information |
| APP 5 | Notification of collection |
| APP 6 | Use or disclosure of personal information |
| APP 11 | Security of personal information |
| APP 12 | Access to personal information |
| APP 13 | Correction of personal information |
| ASIC RG 271 | Internal dispute resolution |

---

## Roadmap

- [ ] Docker containerisation
- [ ] GitHub Actions CI/CD pipeline
- [ ] Render cloud deployment
- [ ] LangSmith tracing and observability
- [ ] DeepEval evaluation framework
- [ ] Azure OpenAI provider support

---

## License

MIT License — see [LICENSE](LICENSE) for details.
