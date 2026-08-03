# SupportLens AI Data Strategy

## Goals

The data plan is designed to be public, reproducible, reviewable, and safe to share in a public repository. SupportLens uses a mixed dataset strategy so the project can demonstrate retrieval, grounding, evaluation, and monitoring flows without exposing private data.

## Selected Dataset Design

The project now uses three complementary document layers and two case-data sources:

1. Synthetic support cases for controlled benchmark design.
2. Public Bitext-derived support cases for broader real-world phrasing coverage.
3. Synthetic support policy documents.
4. Synthetic internal resolution playbooks.

Committed data files in the repository:

- `data/sample/support_cases.jsonl`
- `data/sample/public_support_cases_bitext.jsonl`
- `data/sample/support_policies.jsonl`
- `data/sample/resolution_playbooks.jsonl`
- `data/sample/evaluation_questions.jsonl`
- `data/sample/evaluation_questions_hard.jsonl`
- `data/sample/source_manifest.md`

Public dataset source used for the public sample:

- Hugging Face dataset: `bitext/Bitext-customer-support-llm-chatbot-training-dataset`
- License: `cdla-sharing-1.0`
- Source fields: `flags`, `instruction`, `category`, `intent`, `response`

The repository commits only a reviewer-friendly transformed sample, not the full 26K-row raw dataset.

## Why This Data Is Suitable for a Customer-Support RAG Agent

This mix matches the core retrieval problem faced by support teams:

- synthetic support cases provide tightly controlled examples for benchmark design and expected-ID evaluation;
- public Bitext support cases provide broader customer wording, paraphrases, and distractor material;
- policies provide rule-based constraints that determine what an agent can promise or approve;
- playbooks provide action-oriented internal guidance for troubleshooting, de-escalation, and escalation.

Using all of these sources lets the project evaluate both targeted retrieval quality and the impact of noisier real-world support language.

## Data Schemas

### Support cases schema

Each support case record includes:

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
- `source_dataset` optional
- `source_license` optional
- `source_record_id` optional

How this schema helps:

- `customer_message` supports lexical and semantic retrieval;
- `category`, `intent`, and `product_area` support filtering and monitoring;
- `resolution_summary` and `agent_response` support answer drafting and evaluation;
- provenance fields distinguish synthetic versus public records.

Bitext mapping used by the public sample:

- `instruction` -> `customer_message`
- `category` -> `category`
- `intent` -> `intent`
- `response` -> `agent_response`
- shortened `response` -> `resolution_summary`
- synthetic metadata -> `priority`, `status`, `created_at`
- `source_dataset` -> `bitext/Bitext-customer-support-llm-chatbot-training-dataset`
- `source_license` -> `cdla-sharing-1.0`
- row index provenance -> `source_record_id`

### Support policies schema

Each policy record includes:

- `policy_id`
- `title`
- `category`
- `policy_text`
- `effective_date`
- `source_type`

How this schema helps:

- policy text is a primary grounding source for customer-facing constraints;
- categories support targeted retrieval and analytics;
- effective dates support future versioning and change management.

### Resolution playbooks schema

Each playbook record includes:

- `playbook_id`
- `title`
- `category`
- `trigger_conditions`
- `recommended_steps`
- `escalation_rules`
- `source_type`

How this schema helps:

- trigger conditions support matching internal actions to support scenarios;
- recommended steps provide structured guidance for answer generation;
- escalation rules support safer handling of high-risk or unresolved cases.

## Public-Data Extension Plan

The selected public-data extension for this submission is Bitext. The project includes two reproducible options:

1. committed public sample file for reviewers;
2. optional adapter command to re-download and transform a larger local Bitext subset into ignored `data/processed/` output.

Current public-data command:

```bash
python -m src.ingestion.public_datasets --source bitext --limit 300
```

Future extension can add:

- larger local Bitext slices for deeper retrieval stress tests;
- additional open support-style datasets mapped into the same schema;
- richer public-data provenance and category normalization rules.

## Synthetic-Data Governance Note

The synthetic benchmark cases, policies, and playbooks are authored or generated for this repository. The public Bitext cases are from a public dataset and remain placeholder-style synthetic support language rather than private customer data.

Governance rules for this repository:

- no private support tickets;
- no real customer PII intentionally included;
- no private company information;
- no DataTalksClub FAQ data;
- no committed secrets.

## How the Dataset Supports Retrieval Evaluation

The dataset supports two complementary evaluation goals:

- controlled measurement through the synthetic evaluation question files;
- tougher retrieval conditions through public Bitext distractor cases in combined mode.

The synthetic evaluation sets in `data/sample/evaluation_questions.jsonl` and `data/sample/evaluation_questions_hard.jsonl` still define the expected relevant IDs for Hit Rate and MRR. The Bitext public sample does not change those expected IDs; it adds broader customer language and more non-answer distractors.

## How the Dataset Supports LLM Evaluation

The data supports future answer evaluation by combining:

- public support phrasing from Bitext;
- synthetic policy constraints;
- synthetic playbook guidance;
- controlled expected IDs from the synthetic benchmark.

This makes it possible to compare prompts based on whether a generated answer:

- addresses the user request;
- remains grounded in retrieved evidence;
- respects policy constraints;
- cites the correct support sources.

## How the Dataset Supports Monitoring

The structured fields support future monitoring and dashboarding:

- `category`, `intent`, and `product_area` support topic charts;
- `priority` supports risk-oriented analysis;
- provenance fields support synthetic-versus-public tracking;
- source-type usage can show whether answers lean more on cases, policies, or playbooks.

## Data Governance Constraints

- No private support data.
- No committed raw Bitext full dataset.
- No repository secrets.
- No DataTalksClub FAQ data.

## Data Layers

- `data/raw/` for non-committed or externally sourced raw artifacts.
- `data/processed/` for generated intermediate outputs, typically ignored from git.
- `data/sample/` for small committed examples safe for reviewers.

## Planned Metadata Strategy

Every stored document or chunk is expected to carry metadata such as:

- source type;
- source identifier;
- support category;
- product area when relevant;
- timestamp or effective date;
- chunk identifier;
- synthetic or public provenance marker;
- source dataset and license where relevant.
