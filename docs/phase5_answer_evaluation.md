# Phase 5A Answer Evaluation

## Phase 5A Scope

Phase 5A implements the answer-quality evaluation framework and validates it in dry-run mode.

This phase validates the evaluation framework and dry-run answer structure. It does not yet provide final live LLM quality scores because the configured Qwen account returned a provider-side quota/billing error during Phase 4 validation.

## Why Real LLM Evaluation Is Currently Pending

The OpenAI-compatible Qwen models endpoint was reachable during Phase 4 troubleshooting once local proxy variables were removed for the process. However, the live chat request was blocked by a provider-side 403 quota/billing response.

Because of that, Phase 5A focuses on reproducible dry-run evaluation rather than claiming final live LLM answer quality.

## Dry-Run Answer Evaluation Method

The Phase 5A runner:

1. loads a committed evaluation question set;
2. runs the Phase 4 answer pipeline in `--dry-run` mode for each question;
3. collects answer text, citations, evidence, and metadata;
4. computes transparent non-LLM quality checks;
5. writes ignored local detailed and summary outputs.

CLI examples:

```bash
python -m src.evaluation.run_answer_evaluation --eval-file data/sample/evaluation_questions.jsonl --top-k 5 --dry-run
python -m src.evaluation.run_answer_evaluation --eval-file data/sample/evaluation_questions_hard.jsonl --top-k 5 --dry-run
```

## Quality Checks Implemented

The evaluation framework checks:

- citation presence;
- citation validity;
- unsupported citation IDs;
- evidence count;
- retrieved source overlap with expected source IDs;
- answer section completeness;
- minimum answer length;
- excessive answer length flag;
- insufficient evidence flag;
- grounding proxy score based on citation validity, source overlap, and section completeness.

## Metrics Produced

The summary output includes:

- `eval_file`
- `question_count`
- `top_k`
- `dry_run`
- `retrieval_method`
- `prompt_version`
- `average_source_overlap_rate`
- `average_citation_validity_rate`
- `average_grounding_proxy_score`
- `basic_quality_pass_rate`
- `section_completeness_rate`
- `timestamp`

## Prompt Variants Prepared for Future Comparison

Prompt variants are now defined for future live comparison:

- `baseline_grounded`
- `concise_support`
- `policy_first`

Phase 5A records the prompt version in run metadata even when operating in dry-run mode.

## Results From Original Evaluation Set

`top_k = 5`, `dry_run = true`, `prompt_version = baseline_grounded`

- question count: 14
- average source overlap rate: 0.6881
- average citation validity rate: 1.0000
- average grounding proxy score: 0.8960
- basic quality pass rate: 1.0000
- section completeness rate: 1.0000

## Results From Hard Evaluation Set

`top_k = 5`, `dry_run = true`, `prompt_version = baseline_grounded`

- question count: 12
- average source overlap rate: 0.5972
- average citation validity rate: 1.0000
- average grounding proxy score: 0.8657
- basic quality pass rate: 1.0000
- section completeness rate: 1.0000

## Limitations

- These are dry-run structural and grounding-proxy metrics, not live model quality scores.
- Citation validity is measured against emitted citation IDs, not semantic correctness of each claim.
- Source overlap is still tied to the synthetic benchmark design.
- Live prompt comparison remains pending provider quota access.

## Phase 5B Plan

Recommended Phase 5B focus after quota access is fixed:

- run live LLM answer generation on the same benchmark sets;
- compare `baseline_grounded`, `concise_support`, and `policy_first` prompts;
- add deeper groundedness and citation-correctness review;
- compare dry-run structural outcomes against live model behavior.