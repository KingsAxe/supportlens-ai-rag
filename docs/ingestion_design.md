# SupportLens AI Ingestion Design

## Target Ingestion Flow

```text
synthetic sample files and/or public Bitext sample
-> schema validation
-> text normalization
-> provenance enrichment
-> chunk preparation
-> storage-ready documents
-> keyword/vector indexing inputs
```

The repository now implements a lightweight local ingestion baseline and keeps the storage design future-facing for PostgreSQL plus pgvector.

## Expected Input Files

Current committed inputs:

- `data/sample/support_cases.jsonl`
- `data/sample/public_support_cases_bitext.jsonl`
- `data/sample/support_policies.jsonl`
- `data/sample/resolution_playbooks.jsonl`
- `data/sample/evaluation_questions.jsonl`
- `data/sample/evaluation_questions_hard.jsonl`

Optional local transform command:

```bash
python -m src.ingestion.public_datasets --source bitext --limit 300
```

This command downloads the Bitext CSV when reachable, maps it into the SupportLens support-case schema, and writes ignored output to `data/processed/public_support_cases_bitext.jsonl`.

## Implemented Ingestion Modes

```bash
python -m src.ingestion.pipeline --sample
python -m src.ingestion.pipeline --public-sample
python -m src.ingestion.pipeline --combined-sample
```

Mode definitions:

- `--sample`: synthetic support cases plus synthetic policies and playbooks.
- `--public-sample`: Bitext public support cases plus synthetic policies and playbooks.
- `--combined-sample`: synthetic cases, Bitext public cases, and synthetic policies and playbooks.

`--combined-sample` is the recommended mode for local retrieval experiments because it keeps the controlled benchmark records while adding broader public-language distractors.

## Validation Rules

### Support cases

- every record must have a unique `case_id`;
- required fields must be present and non-empty;
- `created_at` must use ISO date formatting;
- optional provenance fields such as `source_dataset`, `source_license`, and `source_record_id` must be non-empty when present;
- no obvious real PII should appear in `customer_message`, `resolution_summary`, or `agent_response`.

### Support policies

- every record must have a unique `policy_id`;
- `title`, `category`, `policy_text`, `effective_date`, and `source_type` must be present;
- policy text should be descriptive enough for chunk-based retrieval.

### Resolution playbooks

- every record must have a unique `playbook_id`;
- `title`, `category`, `trigger_conditions`, `recommended_steps`, `escalation_rules`, and `source_type` must be present;
- escalation rules should be explicit enough for grounded answer generation.

### Evaluation questions

- every record must have a unique `question_id`;
- the question must map to at least one expected relevant document ID across cases, policies, or playbooks;
- referenced document IDs must exist in the controlled synthetic benchmark files.

## Chunking Strategy

Current chunking rules remain intentionally simple and deterministic:

- support cases are one chunk each;
- policies are split by paragraph boundaries, then fixed-size only if needed;
- playbooks are split by their logical text sections.

This keeps retrieval traceability straightforward while the project remains in the local baseline phase.

## Metadata Strategy

Every stored document or chunk carries metadata such as:

- document type: case, policy, or playbook;
- source ID;
- category;
- intent or product area when relevant;
- date field such as `created_at` or `effective_date`;
- chunk index and parent document ID;
- provenance marker such as `synthetic_sample` or `public_sample`;
- optional source dataset and license fields for public records.

## Future dlt Option

A future ingestion implementation may use `dlt` if it improves reproducibility, pipeline structure, and destination handling. This is optional, not required for the project.

A reasonable future `dlt` use case would be:

- loading larger public support-style source files;
- normalizing to the project schemas;
- writing validated records into PostgreSQL or intermediate tables.

## Target Storage Design for Local and Docker Mode

Current practical local storage:

- source JSONL files under `data/sample/`;
- ignored generated outputs under `data/processed/`;
- optional local public dataset transforms under `data/processed/`.

Primary planned storage target for the full app:

- PostgreSQL with `pgvector` for the main local and Docker-based stack.

Pragmatic early-development fallback remains:

- local JSONL files for raw and sample inputs;
- SQLite only if needed for quick validation or experiments and clearly documented as temporary.

## Target Storage Design for Cloud Mode

Planned cloud storage options:

- Cloud SQL for PostgreSQL as the main managed database path on GCP;
- alternatively, a hosted PostgreSQL plus `pgvector` provider if it simplifies deployment.

Cloud design goals:

- same logical schema as local development;
- reproducible migration path from local Docker to cloud deployment;
- externalized secrets and runtime configuration;
- support for retrieval logging and feedback storage alongside document indexes.
