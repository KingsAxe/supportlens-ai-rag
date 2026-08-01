# SupportLens AI Project Plan

## Phase 0: Scaffold and Documentation Blueprint

**Objective**

Create the repository scaffold, placeholder application structure, and planning documents without implementing the full system.

**Deliverables**

- Project directory structure.
- Placeholder app, module, Docker, and config files.
- README skeleton.
- Architecture, data, evaluation, monitoring, deployment, and project plan docs.

**Validation checks**

- Required directories and files exist.
- `git status --short` reflects only intended unstaged changes.
- `git diff --check` reports no whitespace or merge-marker issues.

**Expected files**

- `README.md`
- `app/`
- `src/`
- `data/`
- `docs/`
- `Dockerfile`
- `docker-compose.yml`
- `pyproject.toml`
- `.env.example`
- `.gitignore`

## Phase 1: Dataset and Ingestion

**Objective**

Define the initial reproducible data sources and implement ingestion for sample support cases and support knowledge documents.

**Deliverables**

- Chosen public or synthetic dataset specification.
- Sample raw files in `data/sample/`.
- Initial ingestion scripts or modules.
- Processed output schema definition.

**Validation checks**

- Raw input can be parsed deterministically.
- Processed records contain stable IDs and metadata.
- Sample run produces output in `data/processed/`.

**Expected files**

- `src/ingestion/*`
- `data/sample/*`
- `data/processed/*`
- `docs/data_strategy.md`

## Phase 2: Knowledge Base and Retrieval

**Objective**

Build the searchable knowledge base and baseline retrieval pipeline.

**Deliverables**

- Document chunking logic.
- Keyword indexing path.
- Vector indexing path.
- Baseline retrieval interface.

**Validation checks**

- Known test queries return plausible evidence.
- Chunk metadata remains traceable to original sources.
- Index build and retrieval runs are reproducible.

**Expected files**

- `src/retrieval/*`
- `src/db/*`
- `tests/*`

## Phase 3: Retrieval Evaluation

**Objective**

Evaluate retrieval quality across multiple retrieval strategies.

**Deliverables**

- Evaluation dataset or labeled query set.
- Retrieval benchmark scripts.
- Comparison outputs for keyword, vector, hybrid, and reranked retrieval.

**Validation checks**

- Hit Rate and MRR are computed consistently.
- Evaluation runs are reproducible from documented inputs.
- Results are saved for later reporting.

**Expected files**

- `src/evaluation/*`
- `notebooks/*`
- `docs/evaluation_plan.md`

## Phase 4: RAG Answer Generation

**Objective**

Add grounded answer generation on top of retrieved evidence.

**Deliverables**

- Prompt templates.
- Citation-aware response generation flow.
- Query rewriting integration.

**Validation checks**

- Generated outputs include source citations.
- Retrieval context passed to the LLM is inspectable.
- Example queries produce grounded rather than generic answers.

**Expected files**

- `src/rag/*`
- `tests/*`

## Phase 5: LLM Evaluation

**Objective**

Evaluate generated answers for quality and grounding.

**Deliverables**

- Answer evaluation rubric.
- Prompt version comparison workflow.
- Saved evaluation outputs.

**Validation checks**

- Relevance, groundedness, and citation correctness can be reviewed.
- Prompt variants are comparable on the same evaluation set.
- Evaluation results are documented clearly.

**Expected files**

- `src/evaluation/*`
- `docs/evaluation_plan.md`
- `notebooks/*`

## Phase 6: Streamlit UI

**Objective**

Implement the user-facing interface for asking questions and reviewing results.

**Deliverables**

- Main question-answer interface.
- Retrieval evidence display.
- Citation display.

**Validation checks**

- UI can run locally.
- Core flows render without crashes.
- Retrieved evidence and citations are visible to the user.

**Expected files**

- `app/streamlit_app.py`
- `app/pages/*`

## Phase 7: Feedback and Monitoring Dashboard

**Objective**

Capture user feedback and expose operational and quality metrics.

**Deliverables**

- Feedback logging pipeline.
- Monitoring dataset or table design.
- Dashboard page for quality and usage metrics.

**Validation checks**

- Feedback events are persisted.
- Dashboard metrics reflect logged events.
- Key charts render from real application records.

**Expected files**

- `src/monitoring/*`
- `app/pages/2_Monitoring_Dashboard.py`
- `docs/monitoring_plan.md`

## Phase 8: Docker Compose

**Objective**

Containerize the application for reproducible local execution.

**Deliverables**

- Functional `Dockerfile`.
- Functional `docker-compose.yml`.
- Documented local startup flow.

**Validation checks**

- Local stack starts successfully.
- Required services can communicate.
- Environment variable handling avoids committed secrets.

**Expected files**

- `Dockerfile`
- `docker-compose.yml`
- `README.md`

## Phase 9: GCP Cloud Run Deployment

**Objective**

Prepare and validate a deployment path for GCP.

**Deliverables**

- Build and deployment instructions.
- Secret handling approach.
- Chosen managed storage/database approach.

**Validation checks**

- Deployment steps are documented end to end.
- Runtime configuration requirements are explicit.
- Deployment checklist can be followed without repository secrets.

**Expected files**

- `docs/deployment_gcp.md`
- `README.md`

## Phase 10: Final Documentation, Screenshots, and Submission

**Objective**

Finalize the project package for review and submission.

**Deliverables**

- Final README updates.
- Screenshots or demo visuals.
- Final evaluation and monitoring summaries.
- Submission-ready documentation.

**Validation checks**

- Reviewer can understand setup and outcomes quickly.
- Reported functionality matches verified implementation.
- Submission materials align with Zoomcamp requirements.

**Expected files**

- `README.md`
- `docs/*`
- `app/pages/3_Evaluation_Report.py`