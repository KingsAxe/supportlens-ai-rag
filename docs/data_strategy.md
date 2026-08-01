# SupportLens AI Data Strategy

## Goals

The data plan is designed to be public, reproducible, reviewable, and safe to share in a public repository. Phase 1 uses a synthetic but realistic support-intelligence dataset so the project can demonstrate retrieval, grounding, evaluation, and monitoring flows without exposing private data.

## Selected Dataset Design

The initial dataset design uses three complementary document layers:

1. Customer support cases or utterances stored as structured JSONL records.
2. Support policy documents stored as policy-centric JSONL records.
3. Resolution playbooks stored as internal guidance JSONL records.

Committed sample files in this phase:

- `data/sample/support_cases.jsonl`
- `data/sample/support_policies.jsonl`
- `data/sample/resolution_playbooks.jsonl`
- `data/sample/evaluation_questions.jsonl`
- `data/sample/source_manifest.md`

## Why This Data Is Suitable for a Customer-Support RAG Agent

This design matches the core retrieval problem faced by support teams:

- support cases provide prior examples of customer language, issue framing, and successful resolutions;
- policies provide rule-based constraints that determine what an agent can promise or approve;
- playbooks provide action-oriented internal guidance for troubleshooting, de-escalation, and escalation.

Using all three layers allows the future RAG system to answer both factual and procedural questions while grounding responses in explicit sources.

## Data Schemas

### Support cases schema

Each support case record is designed to include:

- `case_id`
- `customer_message`
- `category`
- `intent`
- `product_area`
- `priority`
- `status`
- `resolution_summary`
- `agent_response`
- `created_at`

Why this schema helps:

- `customer_message` supports semantic and lexical matching;
- `category`, `intent`, and `product_area` support filtering and monitoring;
- `resolution_summary` and `agent_response` support answer drafting and evaluation;
- `priority` and `status` support operational analysis.

### Support policies schema

Each policy record is designed to include:

- `policy_id`
- `title`
- `category`
- `policy_text`
- `effective_date`
- `source_type`

Why this schema helps:

- policy text is a primary grounding source for customer-facing constraints;
- categories support targeted retrieval and analytics;
- effective dates support future versioning and change management.

### Resolution playbooks schema

Each playbook record is designed to include:

- `playbook_id`
- `title`
- `category`
- `trigger_conditions`
- `recommended_steps`
- `escalation_rules`
- `source_type`

Why this schema helps:

- trigger conditions support matching internal actions to support scenarios;
- recommended steps provide structured guidance for answer generation;
- escalation rules support safer handling of high-risk or unresolved cases.

## Public-Data Extension Plan

The committed sample data is synthetic and intentionally small. Future extension can add public support-style data sources while keeping the same schemas or mapping into them.

Planned extension path:

1. identify a public support-conversation or helpdesk-style dataset with reproducible access;
2. normalize public records into the support-case schema;
3. preserve provenance metadata marking each record as public or synthetic;
4. augment the sample policies and playbooks with additional authored support knowledge documents.

Selection criteria for public data:

- open availability;
- reproducible acquisition path;
- suitability for support-style retrieval;
- no private or restricted content.

## Synthetic-Data Governance Note

All Phase 1 sample records are synthetic. They are designed to resemble realistic support operations without referencing any real customer, employee, company account, or internal document.

Governance rules for synthetic data in this repository:

- no real names linked to personal details;
- no real email addresses, phone numbers, account numbers, or addresses;
- no private company information;
- no DataTalksClub FAQ data.

## How the Dataset Supports Retrieval Evaluation

The support cases, policies, and playbooks are intentionally cross-linked by category and issue type. This supports retrieval evaluation because a single question may have:

- relevant historical cases for precedent;
- relevant policies for constraints;
- relevant playbooks for internal next steps.

The evaluation seed set in `data/sample/evaluation_questions.jsonl` maps each question to expected relevant document IDs for Hit Rate and MRR benchmarking across keyword, vector, hybrid, and reranked retrieval.

## How the Dataset Supports LLM Evaluation

The dataset supports future answer evaluation by providing distinct evidence types:

- support cases help assess example-based answer relevance;
- policies help assess groundedness and citation correctness;
- playbooks help assess procedural completeness and escalation quality.

This makes it possible to compare prompts based on whether the generated answer:

- addresses the user’s need;
- stays within policy limits;
- references the correct supporting documents;
- includes appropriate escalation guidance when necessary.

## How the Dataset Supports Monitoring

The structured fields support future monitoring and dashboarding:

- `category`, `intent`, and `product_area` support top-topic charts;
- `priority` supports risk-oriented analysis;
- document provenance supports synthetic versus public-data tracking;
- retrieval matches against cases, policies, and playbooks can be logged to understand source usage patterns.

## Data Governance Constraints

- No private support data.
- No customer PII intentionally included.
- No repository secrets.
- No DataTalksClub FAQ data.

## Data Layers

- `data/raw/` for non-committed or externally sourced raw artifacts.
- `data/processed/` for generated intermediate outputs, typically ignored from git.
- `data/sample/` for small committed examples safe for reviewers.

## Planned Metadata Strategy

Each document or chunk is expected to carry metadata such as:

- source type;
- source identifier;
- support category;
- product area when relevant;
- timestamp or effective date;
- chunk identifier;
- synthetic or public provenance marker.