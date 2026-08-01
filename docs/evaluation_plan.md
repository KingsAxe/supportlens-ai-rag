# SupportLens AI Evaluation Plan

## Retrieval Evaluation Scope

The retrieval layer will be evaluated across four planned strategies:

- keyword retrieval evaluation;
- vector retrieval evaluation;
- hybrid retrieval evaluation;
- reranked retrieval evaluation.

## Retrieval Metrics

Primary planned retrieval metrics:

- Hit Rate;
- MRR.

Additional metrics may be added later if they improve clarity without overcomplicating the benchmark.

## Retrieval Evaluation Design

Planned approach:

1. Build a labeled or semi-labeled query set representing realistic support-agent questions.
2. Define expected relevant cases, policies, or playbook chunks.
3. Run each retrieval strategy on the same evaluation set.
4. Compare result quality and coverage before and after reranking.

## LLM Evaluation Scope

Planned answer-level evaluation dimensions:

- LLM answer relevance;
- groundedness;
- citation correctness;
- prompt version comparison.

## LLM Evaluation Design

The answer evaluation workflow is planned to:

- use the same or overlapping benchmark queries from retrieval evaluation;
- compare prompt versions under consistent retrieval context;
- inspect whether claims are supported by retrieved evidence;
- verify that citations point to the correct supporting documents or chunks.

## Planned Outputs

Planned artifacts include:

- benchmark tables;
- strategy comparison summaries;
- prompt comparison notes;
- evaluation dashboard content or report pages.