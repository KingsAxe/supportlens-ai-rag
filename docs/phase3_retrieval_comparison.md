# Phase 3 Retrieval Comparison

## Phase 3 Scope

Phase 3 expands retrieval beyond the Phase 2 keyword baseline by adding:

- a harder synthetic retrieval benchmark;
- local vector retrieval;
- hybrid retrieval;
- lightweight reranking;
- comparative evaluation across methods.

## Why the Original Baseline Was Too Easy

The original evaluation set is still useful for regression checks, but it is small and tightly aligned with the initial synthetic documents. That made it possible for multiple methods to reach perfect Hit Rate and MRR, which is acceptable as a controlled baseline but not strong evidence of retrieval robustness.

## Harder Evaluation Set Design

`data/sample/evaluation_questions_hard.jsonl` adds 12 harder questions with:

- indirect phrasing;
- multi-source expectations;
- synonym-heavy wording;
- escalation and risk scenarios;
- questions where policy and playbook evidence should both be helpful.

## Vector Retrieval Approach

The vector retriever is configured to use `sentence-transformers/all-MiniLM-L6-v2` when the local dependency is available.

To keep the project runnable without API keys or paid services, the implementation also includes an offline sklearn fallback path using:

- TF-IDF features;
- Truncated SVD for dense projections;
- cosine similarity retrieval.

Chunk text is enriched with title, category, and selected metadata hints to help the local semantic path handle paraphrased questions more effectively.

Validation note:

- The Phase 3 validation run used the local offline vector fallback because `sentence-transformers` was not installed in the current validation environment. The vector module is configured to use `sentence-transformers/all-MiniLM-L6-v2` when the dependency and model are available.

## Hybrid Retrieval Approach

Hybrid retrieval uses Reciprocal Rank Fusion over the keyword and vector result lists. This keeps the implementation simple while allowing the system to benefit from both lexical precision and semantic similarity.

## Reranking Approach

The Phase 3 reranker is intentionally lightweight and fully local. It combines:

- lexical overlap with the query;
- metadata overlap such as category and intent terms;
- rank-based signals from keyword and vector retrieval;
- a small source diversity bonus.

This is a temporary reranking strategy and can later be replaced with a stronger local or cross-encoder reranker.

## Metrics Comparison

### Original evaluation set

`top_k = 5`

| Method | Hit Rate | MRR |
| --- | --- | --- |
| keyword | 1.0000 | 1.0000 |
| vector | 1.0000 | 0.9643 |
| hybrid | 1.0000 | 1.0000 |
| hybrid_rerank | 1.0000 | 1.0000 |

### Hard evaluation set

`top_k = 5`

| Method | Hit Rate | MRR |
| --- | --- | --- |
| keyword | 0.9167 | 0.8125 |
| vector | 1.0000 | 0.8542 |
| hybrid | 1.0000 | 0.8472 |
| hybrid_rerank | 1.0000 | 0.8611 |

## Recommended Retrieval Method

The current recommendation for the RAG app is `hybrid_rerank`.

Why:

- it preserves the original-set ceiling;
- it matches the best Hit Rate on the hard set;
- it produces the strongest MRR on the hard set among the robust methods;
- it remains fully local and reproducible.

## Limitations

- The benchmark remains synthetic and relatively small.
- The current vector path may use the offline sklearn fallback if `sentence-transformers` is not installed locally.
- The reranker is heuristic rather than model-based.
- The evaluation still uses source ID matching rather than deeper relevance grading.

## Next Steps

Recommended next phase:

- build grounded answer generation on top of `hybrid_rerank`;
- log retrieved evidence and citations explicitly;
- prepare answer-level relevance and groundedness evaluation.