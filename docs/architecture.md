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
-> feedback logging
-> monitoring dashboard
-> Docker/GCP deployment
```

## Current Retrieval-Oriented Components

### Data sources

Current committed sample sources include synthetic support cases, synthetic policy documents, synthetic playbooks, and two synthetic evaluation sets. The design intentionally excludes private data and DataTalksClub FAQ data.

### Ingestion pipeline

The implemented ingestion layer can:

- load sample JSONL files;
- validate schemas and duplicate IDs;
- normalize records into a shared document format;
- create deterministic chunk records;
- persist ignored local processed artifacts for retrieval and evaluation.

### Knowledge base

The current local knowledge base is file-backed under `data/processed/` and includes:

- normalized documents;
- retrieval chunks;
- vector cache artifacts when vector retrieval is used;
- evaluation metric reports.

This is a local development baseline, not the final storage design.

### Retrieval stack

The current retrieval stack includes:

- BM25-style keyword retrieval;
- local vector retrieval with a default sentence-transformers model configuration and an offline sklearn fallback path;
- hybrid retrieval via reciprocal rank fusion;
- a lightweight local reranker using lexical overlap, metadata overlap, and source diversity heuristics.

### Answer generation

Grounded LLM answer generation is still a later phase.

### Feedback and monitoring

Feedback logging and monitoring are still later phases.

### Packaging and deployment

The local target remains Docker Compose in a later phase. The future cloud target is GCP Cloud Run with externalized secrets and managed persistence.