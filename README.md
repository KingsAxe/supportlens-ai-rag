# SupportLens AI

**Production-style customer support intelligence RAG agent for DataTalksClub LLM Zoomcamp 2026**

## Problem Statement

Support teams often need to respond quickly and consistently while navigating historical cases, internal policies, and resolution playbooks. Relevant information is usually scattered across tickets, notes, and support documentation, which makes grounded response generation difficult and slows down agents.

SupportLens AI is planned as a customer support intelligence system that helps support agents retrieve similar historical cases, surface relevant policy and playbook snippets, and generate grounded response recommendations with citations.

## What the System Does

Planned capabilities:

- Retrieve similar historical support cases.
- Retrieve relevant support policy and playbook content.
- Combine keyword and vector retrieval for hybrid search.
- Rewrite user queries to improve retrieval quality.
- Rerank retrieved results before answer generation.
- Generate grounded answer recommendations with citations.
- Collect explicit user feedback on output quality.
- Monitor latency, usage, retrieval behavior, and quality signals.
- Run locally with Docker Compose.
- Support a future deployment path to GCP Cloud Run.

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
- `pyproject.toml` is intentionally minimal.
- `.env.example` contains placeholders only and no real secrets.
- `data/sample/` contains a small synthetic dataset for reviewer-friendly testing.

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

Planned alignment with the final project rubric:

- [x] Problem description
- [x] Dataset or API-backed data source plan
- [x] Data ingestion plan
- [x] RAG or agent application plan
- [x] Retrieval evaluation plan
- [x] LLM evaluation plan
- [x] Application interface plan
- [x] User feedback collection plan
- [x] Monitoring plan
- [x] Docker/containerization plan
- [x] Reproducible setup plan
- [x] Best-practice design for hybrid search, reranking, and query rewriting
- [x] Optional cloud deployment plan

## Current Project Status

Current status as of August 1, 2026:

- Phase 0 scaffold and documentation blueprint is complete.
- Phase 1 sample dataset and ingestion design documents are being prepared.
- No production ingestion pipeline is implemented yet.
- No retrieval pipeline, evaluation pipeline, or UI behavior has been verified yet.

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

Recommended next phase: Phase 2, knowledge base and retrieval implementation on top of the Phase 1 dataset design.