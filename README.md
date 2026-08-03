# SupportLens AI

**Production-style customer support intelligence RAG agent for DataTalksClub LLM Zoomcamp 2026**

## Problem Statement

Support teams often need to respond quickly and consistently while navigating historical cases, internal policies, and resolution playbooks. Relevant information is usually scattered across tickets, notes, and support documentation, which makes grounded response generation difficult and slows down agents.

SupportLens AI is planned as a customer support intelligence system that helps support agents retrieve similar historical cases, surface relevant policy and playbook snippets, and generate grounded response recommendations with citations.

## What the System Does

Implemented in the current local stack:

- Validates the committed synthetic sample dataset.
- Normalizes support cases, policies, and playbooks into a shared document format.
- Prepares deterministic retrieval chunks.
- Runs keyword, vector, hybrid, and hybrid-plus-rerank retrieval evaluation.
- Uses `hybrid_rerank` as the current retrieval method for grounded answer generation.
- Packages retrieval results into citation-ready evidence.
- Builds a grounded support-assistant prompt.
- Supports deterministic dry-run/mock answer generation without API keys.
- Supports real OpenAI-compatible LLM mode when environment variables and dependencies are available.
- Writes ignored local run metadata for later answer evaluation and monitoring work.

Planned later phases:

- Richer answer evaluation.
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

## Retrieval and Grounded Generation

Implemented commands:

```bash
python -m src.ingestion.pipeline --sample
python -m src.retrieval.evaluate --sample --top-k 5 --method hybrid_rerank --eval-file data/sample/evaluation_questions_hard.jsonl
python -m src.rag.answer --question "A customer says they were charged twice after upgrading. What similar cases and policies apply?" --top-k 5 --dry-run
```

Current retrieval summary:

- `hybrid_rerank` is the selected retrieval method for grounded generation.
- The original synthetic set remains a controlled easy baseline.
- The harder set is the more meaningful retrieval comparison benchmark.
- The current answer layer is grounded by retrieved evidence and citation IDs, but it is still an early local baseline.

Validation note:

- The Phase 3 and Phase 4 validation runs used the local offline vector fallback because `sentence-transformers` was not installed in the current validation environment. The vector module is configured to use `sentence-transformers/all-MiniLM-L6-v2` when the dependency and model are available.
- Phase 4 dry-run answer generation was validated successfully. The OpenAI-compatible Qwen models endpoint was reachable when local proxy variables were disabled, but the live chat smoke test was blocked by a provider-side 403 quota/billing response. Real LLM mode is implemented through environment-based configuration, while dry-run mode remains available for reproducible reviewer testing without an API key.

See [docs/phase3_retrieval_comparison.md](docs/phase3_retrieval_comparison.md) and [docs/phase4_grounded_generation.md](docs/phase4_grounded_generation.md).

## Planned Evaluation

Evaluation currently covers:

- retrieval comparison metrics;
- answer-shape and citation validation hooks;
- local run metadata capture for later answer evaluation.

See [docs/evaluation_plan.md](docs/evaluation_plan.md).

## Planned Monitoring

Monitoring is still a later phase. See [docs/monitoring_plan.md](docs/monitoring_plan.md).

## Docker and Reproducibility

This repository still uses placeholder Docker files in the current phase.

- `pyproject.toml` now declares local retrieval and LLM-client dependencies.
- `.env.example` contains placeholders only and no real secrets.
- `data/processed/` is used for ignored local artifacts such as chunk outputs, metrics, vector caches, and RAG run logs.

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
- [x] Grounded answer-generation baseline
- [x] Retrieval evaluation baseline
- [x] LLM evaluation hook layer
- [ ] Application interface
- [ ] User feedback collection
- [ ] Monitoring implementation
- [ ] Docker/containerization implementation
- [ ] Reproducible deployment setup
- [ ] Optional cloud deployment implementation

## Current Project Status

Current status as of August 3, 2026:

- Phase 0 scaffold and documentation blueprint is complete.
- Phase 1 sample dataset strategy is complete.
- Phase 2 ingestion and keyword retrieval baseline is complete.
- Phase 3 retrieval comparison is complete.
- Phase 4 grounded answer-generation baseline is implemented locally with successful dry-run validation.
- Real LLM mode is implemented, the models endpoint was reachable with proxy variables disabled, but live chat validation is currently blocked by a provider-side quota/billing response.
- UI, monitoring, Docker, and GCP deployment are not implemented yet.

## Next Step

Recommended next phase: Phase 5, answer-quality evaluation and groundedness analysis.