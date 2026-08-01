# SupportLens AI

**Production-style customer support intelligence RAG agent for DataTalksClub LLM Zoomcamp 2026**

## Problem Statement

Support teams often need to respond quickly and consistently while navigating historical cases, internal policies, and resolution playbooks. Relevant information is usually scattered across tickets, notes, and support documentation, which makes grounded response generation difficult and slows down agents.

SupportLens AI is planned as a customer support intelligence system that helps support agents retrieve similar historical cases, surface relevant policy and playbook snippets, and generate grounded response recommendations with citations.

## What the System Does

Implemented in the current baseline:

- Validates the committed synthetic sample dataset.
- Normalizes support cases, policies, and playbooks into a shared document format.
- Prepares deterministic retrieval chunks.
- Runs a keyword retrieval baseline over the chunk set.
- Evaluates retrieval against the sample benchmark with Hit Rate and MRR.

Planned later phases:

- Vector retrieval and hybrid search.
- Reranking and query rewriting.
- Grounded LLM answer generation with citations.
- Feedback capture, monitoring, UI, Docker deployment, and GCP deployment.

## Architecture Overview

Target architecture:

```text
Data sources
-> ingestion pipeline
-> cleaned/chunked documents
-> keyword index + vector index
-> query rewriting
-> hybrid retrieval
-> reranking
-> grounded LLM answer with citations
-> feedback logging
-> monitoring dashboard
-> Docker/GCP deployment
```

See [docs/architecture.md](docs/architecture.md) for the planned system design.

## Dataset Strategy

The project uses a reproducible support-intelligence dataset design with three data layers:

- Synthetic customer support cases designed for retrieval, evaluation, and answer drafting.
- Synthetic support policy documents that simulate customer-facing rules and constraints.
- Synthetic internal resolution playbooks that simulate agent guidance and escalation paths.

Reviewer-friendly sample files committed in this phase:

- `data/sample/support_cases.jsonl`
- `data/sample/support_policies.jsonl`
- `data/sample/resolution_playbooks.jsonl`
- `data/sample/evaluation_questions.jsonl`
- `data/sample/source_manifest.md`

Constraints:

- No private support data.
- No secrets in the repository.
- No DataTalksClub FAQ data.

See [docs/data_strategy.md](docs/data_strategy.md) for the detailed plan.

## Phase 2 Baseline

The current retrieval baseline is intentionally lightweight:

- `python -m src.ingestion.pipeline --sample` validates sample JSONL, normalizes documents, creates chunks, and writes ignored local outputs under `data/processed/`.
- `python -m src.retrieval.evaluate --sample --top-k 5` runs the keyword baseline and writes ignored local metrics under `data/processed/keyword_retrieval_metrics.json`.

See [docs/phase2_retrieval_baseline.md](docs/phase2_retrieval_baseline.md) for the implementation notes and verified local metrics.

## Planned RAG Flow

Planned application flow:

1. Ingest raw support-style data and internal support knowledge documents.
2. Clean, normalize, and chunk documents.
3. Store documents in a knowledge base with keyword and vector indexes.
4. Rewrite incoming queries when beneficial.
5. Run hybrid retrieval across historical cases and policy/playbook content.
6. Rerank retrieved candidates.
7. Generate grounded response recommendations with citations.
8. Log feedback and operational metadata for monitoring and evaluation.

## Planned Evaluation

Planned evaluation scope:

- Retrieval evaluation for keyword, vector, hybrid, and reranked retrieval.
- Metrics such as Hit Rate and MRR.
- LLM answer evaluation for relevance, groundedness, and citation correctness.
- Prompt version comparisons.
- A seed evaluation set in `data/sample/evaluation_questions.jsonl` for reproducible benchmarking.

See [docs/evaluation_plan.md](docs/evaluation_plan.md).

## Planned Monitoring

Planned monitoring scope:

- User ratings and thumbs up/down feedback.
- Query and retrieval metadata.
- Latency and token usage.
- Number of retrieved documents.
- Low-confidence or weak-grounding flags.
- Category and usage trends in a monitoring dashboard.

See [docs/monitoring_plan.md](docs/monitoring_plan.md).

## Docker and Reproducibility

This phase includes only a placeholder containerization scaffold:

- `Dockerfile` is a TODO placeholder.
- `docker-compose.yml` is a TODO placeholder.
- `pyproject.toml` remains minimal and uses only the Python standard library for the current Phase 2 baseline.
- `.env.example` contains placeholders only and no real secrets.
- `data/sample/` contains the synthetic dataset for reviewer-friendly testing.

Planned reproducibility goals:

- Local development through Docker Compose.
- Clearly documented environment variables.
- Sample data for reviewer-friendly setup.
- Deterministic project structure and documented run steps.

## GCP Deployment

Future deployment is planned for GCP Cloud Run with supporting services such as Artifact Registry, Secret Manager, and a hosted database option.

This phase does not implement cloud deployment.

See [docs/deployment_gcp.md](docs/deployment_gcp.md).

## LLM Zoomcamp Rubric Checklist

Current progress against the final project rubric:

- [x] Problem description
- [x] Dataset or API-backed data source plan
- [x] Data ingestion baseline
- [x] RAG or agent application plan
- [x] Retrieval evaluation baseline
- [x] LLM evaluation plan
- [ ] Application interface
- [ ] User feedback collection
- [ ] Monitoring implementation
- [ ] Docker/containerization implementation
- [ ] Reproducible deployment setup
- [ ] Hybrid search, reranking, and query rewriting implementation
- [ ] Optional cloud deployment implementation

## Current Project Status

Current status as of August 1, 2026:

- Phase 0 scaffold and documentation blueprint is complete.
- Phase 1 sample dataset strategy is complete.
- Phase 2 ingestion and keyword retrieval baseline is implemented and verified locally on the sample dataset.
- Vector retrieval, hybrid retrieval, reranking, LLM generation, UI, monitoring, Docker, and GCP deployment are not implemented yet.

## Repository Structure

```text
supportlens-ai-rag/
  app/
  src/
  data/
  docs/
  notebooks/
  tests/
  docker/
```

## Next Step

Recommended next phase: Phase 3, retrieval evaluation expansion and error analysis for stronger benchmark coverage before adding semantic retrieval.