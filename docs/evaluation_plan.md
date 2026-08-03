# SupportLens AI Evaluation Plan

## Retrieval Evaluation Scope

The retrieval layer is evaluated across four strategies:

- keyword retrieval evaluation;
- vector retrieval evaluation;
- hybrid retrieval evaluation;
- reranked hybrid retrieval evaluation.

## Retrieval Metrics

Primary retrieval metrics:

- Hit Rate;
- MRR.

## Evaluation Sets

The project now uses two committed synthetic evaluation sets:

- `data/sample/evaluation_questions.jsonl`
- `data/sample/evaluation_questions_hard.jsonl`

### Original evaluation set

The original set is a small controlled baseline aligned closely with the initial sample documents. It is useful for regression checking but too easy to treat as strong evidence of production retrieval quality.

### Hard evaluation set

The harder set adds:

- indirect phrasing;
- multi-source questions;
- synonym-heavy wording;
- escalation and risk scenarios;
- questions that benefit from retrieving both policy and playbook material.

## Retrieval Evaluation Design

Current retrieval evaluation workflow:

1. Validate the selected evaluation file.
2. Confirm all expected document IDs exist in the sample source files.
3. Run retrieval for each question.
4. Compare retrieved source IDs against expected case, policy, and playbook IDs.
5. Compute Hit Rate and MRR for each method.

Supported retrieval methods:

- keyword;
- vector;
- hybrid;
- hybrid_rerank.

## Grounded Answer Evaluation Hooks

Phase 4 adds lightweight non-LLM answer evaluation hooks for later use:

- whether an answer contains citations;
- whether citation IDs are valid;
- whether unsupported citation IDs appear;
- answer length;
- evidence count;
- helper overlap checks between retrieved and expected source IDs.

Phase 5A expands this into a reusable dry-run answer-quality framework with:

- section completeness checks;
- source overlap rate;
- citation validity rate;
- grounding proxy score;
- basic quality pass/fail signals.

These checks are still non-LLM and intentionally transparent.

## Current Comparative Use

The retrieval comparison report is written locally to `data/processed/retrieval_comparison_metrics.json` and is intentionally ignored by git.

The grounded answer CLI writes local run metadata to `data/processed/rag_runs.jsonl`, which is likewise ignored.

The dry-run answer evaluation runner writes:

- `data/processed/answer_evaluation_results.jsonl`
- `data/processed/answer_evaluation_summary.json`

These are also ignored by git.

## LLM Evaluation Scope

Planned richer answer-level evaluation dimensions for later phases:

- answer relevance;
- groundedness;
- citation correctness;
- prompt version comparison.

## LLM Evaluation Design

Current status:

- Phase 5A validates the evaluation framework and dry-run answer structure.
- It does not yet provide final live LLM quality scores because the configured Qwen account returned a provider-side quota/billing error during Phase 4 validation.

The later live answer evaluation workflow is planned to:

- reuse retrieval benchmarks from the current question sets;
- compare prompt variants such as `baseline_grounded`, `concise_support`, and `policy_first`;
- inspect whether claims are supported by retrieved evidence;
- verify whether citations match the correct source records.

## Planned Outputs

Planned artifacts include:

- retrieval comparison tables;
- benchmark summaries by method;
- dry-run answer citation and structure summaries;
- future live prompt comparison notes;
- evaluation report content for the application layer.