# SupportLens AI Ingestion Design

## Target Ingestion Flow

```text
sample or public source files
-> schema validation
-> text normalization
-> record enrichment
-> chunk preparation
-> storage-ready documents
-> keyword/vector indexing inputs
```

Phase 1 documents the design only. It does not implement the full ingestion pipeline yet.

## Expected Input Files

Initial committed sample inputs:

- `data/sample/support_cases.jsonl`
- `data/sample/support_policies.jsonl`
- `data/sample/resolution_playbooks.jsonl`
- `data/sample/evaluation_questions.jsonl`

Future inputs may also include:

- downloaded public support-style datasets in `data/raw/`;
- additional synthetic policy files;
- additional synthetic playbook files.

## Validation Rules

Planned validation checks per file type:

### Support cases

- every record must have a unique `case_id`;
- required fields must be present and non-empty;
- `created_at` must use ISO-style date formatting;
- `category`, `intent`, `product_area`, `priority`, and `status` should come from controlled vocabularies where practical;
- no obvious real PII should appear in `customer_message`, `resolution_summary`, or `agent_response`.

### Support policies

- every record must have a unique `policy_id`;
- `title`, `category`, `policy_text`, `effective_date`, and `source_type` must be present;
- policy text should be sufficiently descriptive for chunk-based retrieval;
- `source_type` should clearly identify synthetic or future public/manual provenance.

### Resolution playbooks

- every record must have a unique `playbook_id`;
- `title`, `category`, `trigger_conditions`, `recommended_steps`, `escalation_rules`, and `source_type` must be present;
- step lists should be parseable into chunk-ready text;
- escalation rules should be explicit enough for grounded answer generation.

### Evaluation questions

- every record must have a unique `question_id`;
- the question must map to at least one expected relevant document ID across cases, policies, or playbooks;
- referenced document IDs must exist in the committed sample set.

## Chunking Strategy

Planned chunking rules by document type:

- support cases: treat each case as one primary retrieval unit initially, with optional secondary chunks for long messages or long agent responses;
- support policies: split by logical policy sections or paragraphs to preserve rule-level granularity;
- resolution playbooks: split by trigger context, step sequence, and escalation section to keep operational guidance focused.

General chunking goals:

- preserve traceability to source records;
- avoid mixing unrelated procedures in one chunk;
- retain enough surrounding context for grounded generation;
- support both keyword and vector retrieval.

## Metadata Strategy

Every stored document or chunk is planned to include metadata such as:

- document type: case, policy, or playbook;
- source ID;
- category;
- intent or product area when relevant;
- synthetic or public provenance marker;
- date field such as `created_at` or `effective_date`;
- chunk index and parent document ID.

This metadata will later support filtering, evaluation slicing, monitoring, and citation rendering.

## Future dlt Option

A future ingestion implementation may use `dlt` if it improves reproducibility, pipeline structure, and destination handling. This is optional, not required for the project.

A reasonable future `dlt` use case would be:

- loading public support-style source files;
- normalizing to the project schemas;
- writing validated records into PostgreSQL or intermediate tables.

## Target Storage Design for Local and Docker Mode

Primary planned storage target:

- PostgreSQL with `pgvector` for the main local and Docker-based stack.

Pragmatic early-development fallback:

- local JSONL files for raw and sample inputs;
- SQLite only if needed for quick validation or experiments and clearly documented as temporary.

Planned local storage layers:

- source JSONL files under `data/sample/` or `data/raw/`;
- normalized records in database tables;
- embeddings and chunk metadata in PostgreSQL plus `pgvector`.

## Target Storage Design for Cloud Mode

Planned cloud storage options:

- Cloud SQL for PostgreSQL as the main managed database path on GCP;
- alternatively, a hosted PostgreSQL plus `pgvector` provider if it simplifies deployment.

Cloud design goals:

- same logical schema as local development;
- reproducible migration path from local Docker to cloud deployment;
- externalized secrets and runtime configuration;
- support for retrieval logging and feedback storage alongside document indexes.