# Phase 2 Retrieval Baseline

## Phase 2 Scope

Phase 2 implements the first working ingestion and retrieval baseline for SupportLens AI.

Implemented in this phase:

- sample JSONL loading and validation;
- normalization into a shared document format;
- deterministic chunk preparation;
- keyword retrieval baseline with a lightweight BM25-style scorer;
- retrieval evaluation against the sample benchmark.

Not implemented in this phase:

- vector retrieval;
- hybrid retrieval;
- reranking;
- query rewriting;
- LLM answer generation;
- UI, monitoring, Docker, or GCP deployment.

## Ingestion Pipeline Summary

Command:

```bash
python -m src.ingestion.pipeline --sample
```

The pipeline currently:

1. reads sample JSONL files from `data/sample/`;
2. validates required fields and duplicate IDs;
3. normalizes records into a shared document shape;
4. prepares deterministic chunk records;
5. writes ignored local outputs into `data/processed/`.

Latest local ingestion summary:

- support cases: 24
- policies: 8
- playbooks: 8
- normalized documents: 40
- chunks: 40
- validation status: passed

## Normalized Document Format

Phase 2 uses this shared document shape:

```text
document_id
source_type
source_id
title
category
content
metadata
```

Source type values currently used:

- `case`
- `policy`
- `playbook`

Notes:

- each support case becomes one document;
- each policy becomes one document;
- each playbook becomes one document;
- metadata preserves source-specific fields such as `intent`, `product_area`, `priority`, `status`, and dates where relevant.

## Chunk Format

Phase 2 uses this chunk shape:

```text
chunk_id
document_id
source_type
source_id
chunk_index
text
metadata
```

Current chunking behavior:

- support cases are kept as one chunk each;
- policies and playbooks are split deterministically by paragraph boundaries, then by fixed size only if needed;
- with the current sample data, each source document produced one chunk, so the chunk count matches the document count.

## Keyword Retrieval Approach

Command:

```bash
python -m src.retrieval.evaluate --sample --top-k 5
```

The baseline retriever uses a lightweight BM25-style scoring function implemented directly in project code. It tokenizes chunk text with a simple lowercase alphanumeric tokenizer, computes document frequencies across the chunk set, and scores each query against chunk text.

This is intentionally a first lexical baseline only. It is useful for establishing a reproducible benchmark before adding semantic retrieval later.

## Evaluation Method

The evaluator:

1. ensures processed chunks exist, running sample ingestion when needed;
2. loads `data/processed/chunks.jsonl`;
3. loads `data/sample/evaluation_questions.jsonl`;
4. retrieves top-k chunks for each question;
5. checks retrieved source IDs against expected case, policy, and playbook IDs;
6. computes Hit Rate and MRR.

Matching rules:

- case results are compared to `expected_case_ids`;
- policy results are compared to `expected_policy_ids`;
- playbook results are compared to `expected_playbook_ids`.

## Latest Local Metrics

Latest verified local run with `--top-k 5`:

- evaluation questions: 14
- top_k: 5
- Hit Rate: 1.0000
- MRR: 1.0000

These results are encouraging but should be interpreted cautiously. The current benchmark is small, synthetic, and closely aligned with the sample dataset, so it is not yet a stress test of retrieval robustness.

## Generated Local Outputs

Phase 2 writes the following ignored local files:

- `data/processed/documents.jsonl`
- `data/processed/chunks.jsonl`
- `data/processed/ingestion_summary.json`
- `data/processed/keyword_retrieval_metrics.json`

## Limitations

- The current benchmark is synthetic and relatively easy.
- The current chunking strategy is simple and does not yet optimize long documents.
- Retrieval is lexical only and can overperform on tightly aligned wording while underperforming on paraphrases.
- There is no per-category error analysis or harder negative set yet.

## Next Steps for Phase 3

Recommended Phase 3 focus:

- expand retrieval evaluation coverage with harder questions and distractors;
- add per-category error analysis;
- inspect failure modes at different `top_k` values;
- prepare the benchmark for comparison against future vector and hybrid retrieval baselines.