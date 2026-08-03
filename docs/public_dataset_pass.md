# Public Dataset Pass

## Why Bitext Was Selected

SupportLens needs a public, reproducible support-case source that broadens customer phrasing beyond the small synthetic benchmark. The Bitext customer-support dataset is a good fit because it is public, support-domain specific, and already structured around customer instructions, support categories, intents, and example responses.

## Dataset Source and License

Public source used in this pass:

- Hugging Face dataset: `bitext/Bitext-customer-support-llm-chatbot-training-dataset`
- License: `cdla-sharing-1.0`
- Original fields: `flags`, `instruction`, `category`, `intent`, `response`

## Fields Used

SupportLens uses these Bitext fields:

- `instruction`
- `category`
- `intent`
- `response`

`flags` is retained only indirectly through provenance of the source dataset and is not part of the committed transformed schema.

## Mapping into the SupportLens Schema

The committed public sample maps Bitext rows into the support-case schema:

- `instruction` -> `customer_message`
- `category` -> `category`
- `intent` -> `intent`
- `response` -> `agent_response`
- shortened `response` -> `resolution_summary`
- derived category mapping -> `product_area`
- synthetic severity heuristic -> `priority`
- synthetic completion status -> `status`
- deterministic synthetic date -> `created_at`
- dataset name -> `source_dataset`
- dataset license -> `source_license`
- source row index -> `source_record_id`

The synthetic metadata fields are added only to make the public rows fit the same ingestion and retrieval schema as the rest of the project. They do not claim to be original Bitext annotations.

## Why Only a Sample Is Committed

The full Bitext dataset is roughly 26.9K rows and should not be committed into this repository for the project submission. Instead, SupportLens commits a reviewer-friendly transformed sample that:

- keeps the repository lightweight;
- stays easy to inspect in git;
- remains reproducible;
- provides more realistic retrieval distractors than the tiny synthetic benchmark alone.

## Committed Public Sample

Committed sample file:

- `data/sample/public_support_cases_bitext.jsonl`

The sample is generated deterministically across intents so it covers the available support taxonomy rather than clustering around just one or two categories.

## How to Regenerate or Process Public Data

Optional local transform command:

```bash
python -m src.ingestion.public_datasets --source bitext --limit 300
```

Behavior:

- downloads the Bitext CSV when reachable;
- transforms records into the SupportLens support-case schema;
- writes ignored output to `data/processed/public_support_cases_bitext.jsonl`.

If network access fails, the adapter should be treated as optional and the committed sample file should be used instead.

## Combined-Sample Ingestion Mode

SupportLens now supports:

```bash
python -m src.ingestion.pipeline --sample
python -m src.ingestion.pipeline --public-sample
python -m src.ingestion.pipeline --combined-sample
```

Recommended mode for local experiments:

- `--combined-sample`

Why:

- it keeps the controlled synthetic benchmark cases used by the evaluation files;
- it adds public Bitext customer language as realistic distractors;
- it lets retrieval operate over a broader case set while still using the synthetic policies and playbooks.

## How Combined-Sample Mode Affects Retrieval

The evaluation question files still point to the synthetic benchmark IDs. Combined mode does not change those expected IDs. Instead, it makes retrieval work harder by adding more case documents that can compete with the benchmark documents.

This is useful for demonstrating that the project is not evaluated only on a tiny perfectly aligned synthetic case set.

## Limitations

- The committed public sample is still only a subset of the full Bitext dataset.
- The Bitext cases are public synthetic support examples, not real production tickets.
- Added metadata such as `priority`, `status`, and `created_at` is derived by SupportLens for schema compatibility.
- Policies and playbooks remain SupportLens-authored synthetic documents rather than public Bitext assets.
