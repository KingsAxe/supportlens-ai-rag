# SupportLens AI

**Production-style customer support intelligence RAG agent for DataTalksClub LLM Zoomcamp 2026**

## Problem Statement

Support teams often need to respond quickly and consistently while navigating historical cases, internal policies, and resolution playbooks. Relevant information is usually scattered across tickets, notes, and support documentation, which makes grounded response generation difficult and slows down agents.

SupportLens AI is built as a customer support intelligence system that helps support agents retrieve similar historical cases, surface relevant policy and playbook snippets, and generate grounded response recommendations with citations.

## What the System Does

Implemented in the current local stack:

- Validates the committed synthetic benchmark data and the committed public Bitext-derived sample.
- Supports synthetic-only, public-only, and combined-sample ingestion modes.
- Includes an optional public dataset adapter for Bitext that writes ignored processed JSONL outputs.
- Normalizes support cases, policies, and playbooks into a shared document format.
- Prepares deterministic retrieval chunks.
- Runs keyword, vector, hybrid, and hybrid-plus-rerank retrieval evaluation.
- Uses `hybrid_rerank` as the current retrieval method for grounded answer generation.
- Packages retrieval results into citation-ready evidence.
- Builds grounded support-assistant prompts with named prompt variants.
- Supports deterministic dry-run/mock answer generation without API keys.
- Supports real OpenAI-compatible LLM mode when environment variables and dependencies are available.
- Runs dry-run answer-quality evaluation and writes ignored local evaluation summaries.
- Provides a Streamlit reviewer interface with Ask, Monitoring Dashboard, and Evaluation Report pages.
- Captures local answer-generation and feedback monitoring events for the rubric-required monitoring layer.

Planned later phases:

- Live LLM answer-quality comparison after provider quota access is restored.
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
-> Streamlit reviewer interface
-> feedback logging
-> monitoring dashboard
-> Docker/GCP deployment
```

See [docs/architecture.md](docs/architecture.md) for the retrieval-oriented architecture notes.

## Dataset Strategy

The project uses a reproducible support-intelligence dataset design with three operational layers and two case-data sources:

- Synthetic customer support cases designed for controlled retrieval, evaluation, and answer drafting.
- Public Bitext-derived customer support cases that broaden phrasing coverage and retrieval distractors.
- Synthetic support policy documents that simulate customer-facing rules and constraints.
- Synthetic internal resolution playbooks that simulate agent guidance and escalation paths.

Committed sample files:

- `data/sample/support_cases.jsonl`
- `data/sample/public_support_cases_bitext.jsonl`
- `data/sample/support_policies.jsonl`
- `data/sample/resolution_playbooks.jsonl`
- `data/sample/evaluation_questions.jsonl`
- `data/sample/evaluation_questions_hard.jsonl`
- `data/sample/source_manifest.md`

Public dataset source:

- Hugging Face: `bitext/Bitext-customer-support-llm-chatbot-training-dataset`
- License: `cdla-sharing-1.0`
- Committed asset: transformed reviewer-friendly sample only, not the full raw dataset.

Constraints:

- No private support data.
- No secrets in the repository.
- No DataTalksClub FAQ data.

See [docs/data_strategy.md](docs/data_strategy.md) and [docs/public_dataset_pass.md](docs/public_dataset_pass.md) for details.

## Retrieval, Grounding, Interface, and Monitoring

Implemented commands:

```bash
python -m src.ingestion.pipeline --combined-sample
python -m src.retrieval.evaluate --sample --top-k 5 --method hybrid_rerank --eval-file data/sample/evaluation_questions_hard.jsonl
python -m src.rag.answer --question "A customer says they were charged twice after upgrading. What should support do?" --top-k 5 --dry-run --prompt-version baseline_grounded
python -m src.evaluation.run_answer_evaluation --eval-file data/sample/evaluation_questions_hard.jsonl --top-k 5 --dry-run
streamlit run app/streamlit_app.py
```

Current retrieval and answer summary:

- `hybrid_rerank` is the selected retrieval method for grounded generation.
- `combined-sample` is the recommended ingestion mode for local experimentation and review.
- The harder synthetic set remains the main retrieval comparison benchmark.
- Public Bitext cases add broader customer phrasing without changing the expected IDs in the controlled evaluation files.
- The Streamlit app defaults to dry-run mode and requires explicit knowledge-base preparation for the selected dataset mode.
- Monitoring now captures local answer-generation events, ratings, thumbs feedback, optional comments, and retrieval metadata.

Validation note:

- The Phase 3, Phase 4, and Phase 5A dry-run validation runs used the local offline vector fallback because `sentence-transformers` was not installed in the current validation environment. The vector module is configured to use `sentence-transformers/all-MiniLM-L6-v2` when the dependency and model are available.
- Phase 4 dry-run answer generation was validated successfully. The OpenAI-compatible Qwen models endpoint was reachable when local proxy variables were disabled, but the live chat smoke test was blocked by a provider-side 403 quota or billing response. Real LLM mode is implemented through environment-based configuration, while dry-run mode remains available for reproducible reviewer testing without an API key.

See [docs/phase3_retrieval_comparison.md](docs/phase3_retrieval_comparison.md), [docs/phase4_grounded_generation.md](docs/phase4_grounded_generation.md), [docs/phase5_answer_evaluation.md](docs/phase5_answer_evaluation.md), [docs/public_dataset_pass.md](docs/public_dataset_pass.md), [docs/streamlit_interface.md](docs/streamlit_interface.md), and [docs/monitoring_dashboard.md](docs/monitoring_dashboard.md).

## Evaluation

Evaluation currently covers:

- retrieval comparison metrics;
- answer-shape and citation validation hooks;
- dry-run answer-quality summary metrics;
- local run metadata capture for later answer evaluation;
- a lightweight Streamlit evaluation report page.

See [docs/evaluation_plan.md](docs/evaluation_plan.md).

## Monitoring

Monitoring now includes:

- local JSONL event logging under ignored `data/processed/` outputs;
- feedback capture from the Ask SupportLens page;
- a Streamlit monitoring dashboard with usage, feedback, source mix, and latency charts;
- a synthetic demo monitoring-event seed option for reviewer convenience.

See [docs/monitoring_dashboard.md](docs/monitoring_dashboard.md) and [docs/monitoring_plan.md](docs/monitoring_plan.md).

## Docker and Reproducibility

This repository still uses placeholder Docker files in the current phase.

- `pyproject.toml` declares local retrieval, LLM-client, and Streamlit dependencies.
- `.env.example` contains placeholders only and no real secrets.
- `data/processed/` is used for ignored local artifacts such as chunk outputs, metrics, vector caches, answer evaluation outputs, public dataset transforms, RAG run logs, and monitoring events.

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
- [x] Dry-run answer evaluation framework
- [x] Application interface baseline
- [x] User feedback collection baseline
- [x] Monitoring implementation baseline
- [ ] Live LLM answer evaluation
- [ ] Docker/containerization implementation
- [ ] Reproducible deployment setup
- [ ] Optional cloud deployment implementation

## Current Project Status

Current status as of August 3, 2026:

- Phase 0 scaffold and documentation blueprint is complete.
- Phase 1 sample dataset strategy is complete.
- Phase 2 ingestion and keyword retrieval baseline is complete.
- Phase 3 retrieval comparison is complete.
- Phase 4 grounded answer-generation baseline is complete with successful dry-run validation.
- Phase 5A answer-quality evaluation is implemented and validated in dry-run mode.
- The public dataset pass adds a committed Bitext-derived support-case sample plus optional adapter support for larger local transforms.
- The Streamlit reviewer interface is implemented for local review.
- Feedback capture and monitoring dashboard are now implemented.
- Live LLM evaluation is still blocked by the provider-side quota or billing response observed in Phase 4.
- Docker and GCP deployment are not implemented yet.

## Next Step

Recommended next phase: Docker and final submission packaging.
