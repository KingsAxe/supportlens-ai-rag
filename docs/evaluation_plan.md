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

Phase 1 introduces `data/sample/evaluation_questions.jsonl` as the initial seed benchmark. Each record contains:

- `question_id`
- `question`
- `expected_case_ids`
- `expected_policy_ids`
- `expected_playbook_ids`
- `answer_type`
- `notes`

Planned use of the seed set:

- keyword retrieval evaluation measures whether lexical matching can recover the expected evidence IDs;
- vector retrieval evaluation measures whether semantic similarity can recover the expected evidence IDs;
- hybrid retrieval evaluation compares combined recall against either method alone;
- reranked retrieval evaluation checks whether reranking improves top-position relevance.

Hit Rate will be used to measure whether at least one expected document is returned in the top-k results. MRR will be used to measure how highly the first relevant document is ranked.

## LLM Evaluation Scope

Planned answer-level evaluation dimensions:

- answer relevance;
- groundedness;
- citation correctness;
- prompt version comparison.

## LLM Evaluation Design

The answer evaluation workflow is planned to:

- use the same or overlapping benchmark queries from retrieval evaluation;
- compare prompt versions under consistent retrieval context;
- inspect whether claims are supported by retrieved evidence;
- verify that citations point to the correct supporting documents or chunks.

How the Phase 1 seed set supports answer evaluation:

- expected case IDs help assess whether generated responses use relevant historical precedent;
- expected policy IDs help assess whether generated answers respect policy boundaries;
- expected playbook IDs help assess whether internal guidance and escalation steps are used appropriately.

Groundedness will later be reviewed by checking whether answer claims can be traced to retrieved documents. Citation correctness will be reviewed by checking whether cited IDs correspond to truly relevant records from the seed set.

## Planned Outputs

Planned artifacts include:

- benchmark tables;
- strategy comparison summaries;
- prompt comparison notes;
- evaluation dashboard content or report pages.