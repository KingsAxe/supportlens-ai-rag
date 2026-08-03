# Phase 4 Grounded Generation

## Phase 4 Scope

Phase 4 adds the first grounded answer-generation layer on top of the selected retrieval method: `hybrid_rerank`.

Implemented in this phase:

- retrieval with `hybrid_rerank`;
- citation-ready evidence packaging;
- grounded prompt construction;
- OpenAI-compatible client wrapper;
- deterministic dry-run/mock generation;
- local run metadata logging;
- lightweight answer-evaluation hooks.

Not implemented in this phase:

- Streamlit UI;
- monitoring dashboard;
- Docker deployment;
- GCP deployment;
- full answer-quality scoring.

## RAG Answer Flow

Current answer flow:

1. ensure processed chunks exist;
2. retrieve candidate evidence with `hybrid_rerank`;
3. build citation-ready evidence objects;
4. build a grounded support prompt;
5. generate an answer with either real LLM mode or deterministic mock mode;
6. validate citation structure with local hooks;
7. append run metadata to an ignored local JSONL log.

## Why `hybrid_rerank` Is Used

`hybrid_rerank` is the selected retrieval method because it:

- preserves strong performance on the easy benchmark;
- keeps perfect Hit Rate on the hard benchmark;
- has the strongest hard-set MRR among the robust local retrieval methods;
- demonstrates both hybrid retrieval and reranking for the project rubric.

## Citation Format

Each retrieved evidence item is converted into a citation-ready structure with:

- `citation_id`
- `source_type`
- `source_id`
- `title`
- `category`
- `text`
- `metadata`
- `score`

Citation IDs are stable within each answer run and use the format `[C1]`, `[C2]`, `[C3]`, and so on.

## Prompt Rules

The grounded answer prompt requires the model to:

- answer only from provided evidence;
- cite claims with `[C1]`, `[C2]`, and similar IDs;
- say when evidence is insufficient;
- separate recommended response from support notes;
- avoid inventing policy details;
- keep a professional support tone.

## LLM Configuration

The answer layer reads these environment variables when present:

- `LLM_PROVIDER`
- `LLM_API_KEY`
- `LLM_BASE_URL`
- `LLM_MODEL`

Defaults:

- provider: `mock`
- model: `mock-supportlens`

No secret values are printed or persisted.

## Dry-Run / Mock Mode

Dry-run mode is the validated baseline in the current environment. It:

- does not require API keys;
- does not make external LLM calls;
- produces deterministic structured markdown output from retrieved evidence;
- still logs run metadata for later evaluation work.

## CLI Examples

```bash
python -m src.rag.answer --question "A customer says they were charged twice after upgrading. What similar cases and policies apply?" --top-k 5 --dry-run
python -m src.rag.answer --question "A customer wants to cancel after a failed payment and asks for a refund. How should support respond?" --top-k 5 --dry-run
```

Real mode is supported in code through environment-based configuration. Phase 4 dry-run answer generation was validated successfully. The OpenAI-compatible Qwen models endpoint was reachable when local proxy variables were disabled, but the live chat smoke test was blocked by a provider-side 403 quota/billing response. Real LLM mode is implemented through environment-based configuration, while dry-run mode remains available for reproducible reviewer testing without an API key.

## Sample Outputs Summary

Dry-run questions validated locally:

1. `A customer says they were charged twice after upgrading. What similar cases and policies apply?`
2. `A customer wants to cancel after a failed payment and asks for a refund. How should support respond?`

Observed behavior:

- both runs produced structured markdown answers;
- both runs emitted citation IDs and evidence lists;
- both runs logged local run metadata with provider `mock` and model `mock-supportlens`;
- the retrieved evidence remains useful but still shows that free-form unseen questions can surface mixed-quality context, especially in dry-run mode.

## Limitations

- The current mock generator is deterministic and not a substitute for a real LLM.
- Live chat validation is currently blocked by a provider-side quota/billing response rather than a local code failure.
- Evidence selection is still heuristic and can include partially relevant records for free-form questions.
- The current evaluation hooks check citation structure, not full answer quality.

## Next Steps for Phase 5

Recommended next phase:

- add answer-quality evaluation over generated outputs;
- measure groundedness and citation correctness more deeply;
- compare prompt variants and dry-run versus live-generation behavior when a real LLM configuration is available.