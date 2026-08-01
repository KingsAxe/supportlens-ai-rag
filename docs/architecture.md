# SupportLens AI Architecture

## Target Flow

```text
Data sources
-> ingestion pipeline
-> cleaned/chunked documents
-> keyword index + vector index
-> query rewriting
-> hybrid retrieval
-> reranking
-> grounded LLM answer with citations
-> feedback logging
-> monitoring dashboard
-> Docker/GCP deployment
```

## Planned Components

### Data sources

Planned sources include public support-style conversations, synthetic support policies, and synthetic resolution playbooks. The design intentionally excludes private data and DataTalksClub FAQ data.

### Ingestion pipeline

The ingestion layer is planned to:

- load raw source files or API-backed content;
- normalize schema and metadata;
- clean noisy text;
- segment long documents into chunks;
- persist processed artifacts for reproducible indexing.

### Knowledge base

The knowledge base is planned to contain:

- a keyword-searchable index for lexical matching;
- a vector index for semantic similarity;
- metadata linking chunks to source documents, categories, and support case identifiers.

### Query processing

The retrieval stack is planned to support:

- optional query rewriting;
- hybrid retrieval over keyword and vector indexes;
- candidate reranking before answer generation.

### Answer generation

The LLM layer is planned to:

- consume reranked evidence;
- generate a grounded recommendation for support agents;
- include citations that map back to retrieved sources;
- expose enough metadata for evaluation and monitoring.

### Feedback and monitoring

The application is planned to log:

- user feedback signals;
- retrieval method metadata;
- latency and usage counters;
- confidence or weak-grounding indicators.

### Packaging and deployment

The local target is Docker Compose. The future cloud target is GCP Cloud Run with externalized secrets and a managed persistence option.