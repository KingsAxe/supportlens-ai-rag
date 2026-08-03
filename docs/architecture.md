# SupportLens AI Architecture

## Target Flow

```text
Data sources
-> ingestion pipeline
-> cleaned/chunked documents
-> keyword index + vector index
-> hybrid retrieval
-> reranking
-> grounded LLM answer with citations
-> Streamlit reviewer interface
-> feedback logging
-> monitoring dashboard
-> Docker/GCP deployment
```

## Current Retrieval-Oriented Components

### Data sources

Current committed sample sources include:

- synthetic support cases;
- Bitext-derived public support cases;
- synthetic policy documents;
- synthetic playbooks;
- synthetic evaluation sets.

The design intentionally excludes private data and DataTalksClub FAQ data.

### Ingestion pipeline

The implemented ingestion layer can:

- load sample JSONL files;
- validate schemas and duplicate IDs;
- normalize records into a shared document format;
- create deterministic chunk records;
- support `sample`, `public_sample`, and `combined_sample` modes;
- persist ignored local processed artifacts for retrieval and evaluation.

The Streamlit interface uses `combined-sample` as the default and recommended mode.

### Knowledge base

The current local knowledge base is file-backed under `data/processed/` and includes:

- normalized documents;
- retrieval chunks;
- vector cache artifacts when vector retrieval is used;
- evaluation metric reports;
- RAG run logs;
- monitoring events.

This is a local development baseline, not the final storage design.

### Retrieval stack

The current retrieval stack includes:

- BM25-style keyword retrieval;
- local vector retrieval with a default sentence-transformers model configuration and an offline sklearn fallback path;
- hybrid retrieval via reciprocal rank fusion;
- a lightweight local reranker using lexical overlap, metadata overlap, and source diversity heuristics.

### Grounded answer generation

The current grounded-generation layer can:

- retrieve evidence with `hybrid_rerank`;
- package citation-ready evidence as `[C1]`, `[C2]`, and so on;
- build a grounded support prompt;
- call an OpenAI-compatible LLM when configured;
- fall back to deterministic mock generation when no live LLM configuration is available;
- log run metadata without storing secrets.

### Streamlit reviewer interface

The current app layer provides:

- a landing page;
- an Ask SupportLens page for question answering and feedback capture;
- a monitoring dashboard page for local usage and feedback analytics;
- a lightweight evaluation report page.

The app does not auto-run all ingestion modes on rerun. Knowledge-base preparation is explicit to avoid concurrent writes to shared processed targets.

### Feedback and monitoring

The monitoring layer now logs local answer-generation and feedback-submission events and summarizes them in the Streamlit dashboard through file-backed analytics helpers.

### Packaging and deployment

The local target remains Docker Compose in a later phase. The future cloud target is GCP Cloud Run with externalized secrets and managed persistence.
