# Autonomous Compliance Auditor

AI-powered compliance auditing system that reviews business documents against Australian Privacy Principles (APP) and ASIC Regulatory Guide 271 (RG 271) using Retrieval-Augmented Generation (RAG) and agentic workflows.

## Architecture

```text
User Document
     ↓
Retriever Agent
     ↓
ChromaDB Vector Store
     ↓
Relevant Regulatory Context
     ↓
Auditor Agent
     ↓
Compliance Findings
```

## Features

* Retrieval-Augmented Generation (RAG)
* Semantic search with ChromaDB
* Evidence-based responses with citations
* Compliance gap analysis
* Severity classification and recommendations
* LangGraph agent workflow
* Streamlit interface
* FastAPI backend
* DeepEval evaluation framework
* Docker-ready deployment

## Tech Stack

| Layer           | Technologies          |
| --------------- | --------------------- |
| Language        | Python 3.11           |
| LLM             | OpenAI GPT-4o         |
| Framework       | LangChain, LangGraph  |
| Vector Database | ChromaDB              |
| Embeddings      | sentence-transformers |
| Backend         | FastAPI, Pydantic     |
| Evaluation      | DeepEval              |
| Observability   | LangSmith             |
| UI              | Streamlit             |
| Deployment      | Docker, Render, AWS   |

## Getting Started

Clone the repository

```bash
git clone https://github.com/<username>/autonomous-compliance-auditor.git
cd autonomous-compliance-auditor
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run document ingestion

```bash
python -m app.ingestion
```

Launch the application

```bash
streamlit run app/ui.py
```

## Example Output

```text
SUMMARY:
The draft policy partially satisfies APP requirements.

Finding 1:
Rule: APP 11
Severity: Medium
Issue: Security controls are insufficiently defined.

Recommendation:
Implement stronger safeguards for personal information.
```
