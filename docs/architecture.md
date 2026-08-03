# SupportLens AI Architecture

## Attempt 1 Flow

```text
Synthetic SupportLens cases + Bitext-derived public support cases + synthetic policies/playbooks
-> ingestion pipeline
-> normalized documents
-> deterministic chunks
-> keyword retrieval + vector retrieval
-> hybrid retrieval
-> lightweight reranking
-> grounded answer generation with citations
-> feedback logging
-> monitoring dashboard
-> Streamlit reviewer interface
-> Docker Compose runtime
```

## Data Sources

Current committed sources include:

- synthetic support cases for controlled evaluation
- Bitext-derived public support cases for broader phrasing coverage
- synthetic support policies
- synthetic resolution playbooks
- synthetic evaluation question sets

The dataset design excludes private data, secrets, and DataTalksClub FAQ data.

## Ingestion and Knowledge Base

The implemented ingestion layer:

- reads committed JSONL sample files
- validates required fields and duplicate IDs
- normalizes cases, policies, and playbooks into one document format
- creates deterministic chunk records
- supports `sample`, `public-sample`, and `combined-sample` modes
- writes runtime artifacts to ignored files under `data/processed/`

`combined-sample` is the default reviewer mode because it mixes the controlled synthetic benchmark with the broader Bitext-derived public sample.

## Retrieval Stack

The current retrieval stack includes:

- BM25-style keyword retrieval
- local vector retrieval using sentence-transformers when available, with an offline fallback path
- hybrid retrieval through reciprocal rank fusion
- lightweight reranking based on lexical overlap, metadata cues, and source diversity

The selected retrieval method for the app is `hybrid_rerank`.

## Grounded Generation Layer

The grounded-generation layer:

- retrieves top evidence with `hybrid_rerank`
- packages citations as `[C1]`, `[C2]`, and so on
- builds grounded support prompts with named prompt variants
- supports deterministic dry-run generation by default
- supports OpenAI-compatible live LLM mode when environment configuration is present
- logs run metadata without storing secrets

Live Qwen chat validation remains blocked by a provider-side quota or billing response, so dry-run remains the reproducible default.

## App and Monitoring Layer

The Streamlit app provides:

- a landing page with reviewer instructions
- an Ask SupportLens page for answer generation
- citation and retrieval metadata display
- feedback capture with rating, thumbs, and optional comments
- a monitoring dashboard with local analytics and demo events
- an evaluation report page with current retrieval and answer-quality metrics

The app does not auto-run multiple ingestion modes on rerun. Knowledge-base preparation is explicit so shared `data/processed/` targets are not overwritten by parallel modes.

## Packaging and Deployment

Attempt 1 packaging targets local reproducibility first:

- local Python execution
- Streamlit reviewer app
- Docker Compose startup on `http://localhost:8501`

Future deployment remains planned for GCP Cloud Run with externalized secrets and managed persistence.
