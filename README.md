# SupportLens AI

**Production-style customer support intelligence RAG agent for DataTalksClub LLM Zoomcamp 2026**

## Problem Statement

Support teams often need to respond quickly and consistently while navigating historical cases, internal policies, and resolution playbooks. Relevant information is usually scattered across tickets, notes, and support documentation, which makes grounded response generation difficult and slows down agents.

SupportLens AI is planned as a customer support intelligence system that helps support agents retrieve similar historical cases, surface relevant policy and playbook snippets, and generate grounded response recommendations with citations.

## What the System Does

Implemented in the current local retrieval stack:

- Validates the committed synthetic sample dataset.
- Normalizes support cases, policies, and playbooks into a shared document format.
- Prepares deterministic retrieval chunks.
- Runs a keyword BM25-style retrieval baseline.
- Runs a local vector retrieval path.
- Combines keyword and vector results with hybrid fusion.
- Applies a lightweight local reranker to hybrid candidates.
- Evaluates retrieval methods against both the original and harder synthetic benchmark sets.

Planned later phases:

- Grounded LLM answer generation with citations.
- Feedback capture and monitoring.
- Streamlit UI.
- Docker deployment and GCP deployment.

## Architecture Overview

Target architecture:

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

See [docs/architecture.md](docs/architecture.md) for the retrieval-oriented architecture notes.

## Dataset Strategy

The project uses a reproducible support-intelligence dataset design with three data layers:

- Synthetic customer support cases designed for retrieval, evaluation, and answer drafting.
- Synthetic support policy documents that simulate customer-facing rules and constraints.
- Synthetic internal resolution playbooks that simulate agent guidance and escalation paths.

Committed sample benchmark files:

- `data/sample/support_cases.jsonl`
- `data/sample/support_policies.jsonl`
- `data/sample/resolution_playbooks.jsonl`
- `data/sample/evaluation_questions.jsonl`
- `data/sample/evaluation_questions_hard.jsonl`
- `data/sample/source_manifest.md`

Constraints:

- No private support data.
- No secrets in the repository.
- No DataTalksClub FAQ data.

See [docs/data_strategy.md](docs/data_strategy.md) for the detailed plan.

## Retrieval Baselines

Implemented commands:

```bash
python -m src.ingestion.pipeline --sample
python -m src.retrieval.evaluate --sample --top-k 5 --method keyword
python -m src.retrieval.evaluate --sample --top-k 5 --method vector
python -m src.retrieval.evaluate --sample --top-k 5 --method hybrid
python -m src.retrieval.evaluate --sample --top-k 5 --method hybrid_rerank
python -m src.retrieval.evaluate --sample --top-k 5 --method all --eval-file data/sample/evaluation_questions_hard.jsonl
```

Current retrieval summary:

- Original synthetic set remains a very easy controlled baseline.
- The harder set introduces indirect phrasing, multi-source expectations, and escalation-oriented questions.
- `hybrid_rerank` is the current recommended retrieval method for the next phase because it matches the original-set ceiling while performing best on the harder set MRR.

Validation note:

- The Phase 3 validation run used the local offline vector fallback because `sentence-transformers` was not installed in the current validation environment. The vector module is configured to use `sentence-transformers/all-MiniLM-L6-v2` when the dependency and model are available.

See [docs/phase2_retrieval_baseline.md](docs/phase2_retrieval_baseline.md) and [docs/phase3_retrieval_comparison.md](docs/phase3_retrieval_comparison.md).

## Planned Evaluation

Evaluation currently covers:

- keyword retrieval evaluation;
- vector retrieval evaluation;
- hybrid retrieval evaluation;
- hybrid plus reranking evaluation;
- Hit Rate;
- MRR.

See [docs/evaluation_plan.md](docs/evaluation_plan.md).

## Planned Monitoring

Monitoring is still a later phase. See [docs/monitoring_plan.md](docs/monitoring_plan.md).

## Docker and Reproducibility

This repository still uses placeholder Docker files in the current phase.

- `pyproject.toml` now declares local retrieval dependencies.
- `.env.example` contains placeholders only and no real secrets.
- `data/processed/` is used for ignored local artifacts such as chunk outputs, metrics, and vector caches.

## GCP Deployment

Future deployment is planned for GCP Cloud Run with supporting services such as Artifact Registry, Secret Manager, and a hosted database option.

This phase does not implement cloud deployment.

See [docs/deployment_gcp.md](docs/deployment_gcp.md).

## LLM Zoomcamp Rubric Checklist

Current progress against the final project rubric:

- [x] Problem description
- [x] Dataset or API-backed data source plan
- [x] Data ingestion baseline
- [x] Retrieval baseline and comparison
- [x] Retrieval evaluation baseline
- [x] LLM evaluation plan
- [ ] Application interface
- [ ] User feedback collection
- [ ] Monitoring implementation
- [ ] Docker/containerization implementation
- [ ] Reproducible deployment setup
- [ ] LLM answer generation
- [ ] Optional cloud deployment implementation

## Current Project Status

Current status as of August 2, 2026:

- Phase 0 scaffold and documentation blueprint is complete.
- Phase 1 sample dataset strategy is complete.
- Phase 2 ingestion and keyword retrieval baseline is complete.
- Phase 3 retrieval comparison is implemented locally with keyword, vector, hybrid, and lightweight reranking.
- LLM generation, UI, monitoring, Docker, and GCP deployment are not implemented yet.

## Next Step

Recommended next phase: Phase 4, grounded answer generation on top of the chosen retrieval stack.