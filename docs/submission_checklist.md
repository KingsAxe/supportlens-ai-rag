# SupportLens AI Submission Checklist

## Rubric Coverage

- problem description: covered in `README.md`
- dataset or API-backed data source: synthetic SupportLens data plus Bitext-derived public sample
- ingestion into a knowledge base: implemented with `sample`, `public-sample`, and `combined-sample` modes
- RAG or agent flow: implemented with `hybrid_rerank` retrieval and grounded answer generation
- retrieval evaluation: implemented with original and hard evaluation sets
- LLM evaluation: dry-run answer-quality framework implemented; live LLM comparison pending provider quota access
- application interface: Streamlit landing, Ask, Monitoring Dashboard, and Evaluation Report pages
- user feedback collection: implemented on the Ask page
- monitoring: implemented with local JSONL logs and Streamlit charts
- Docker or containerization: Dockerfile and Docker Compose provided
- reproducible setup: local commands, Docker commands, and ignored runtime artifacts documented
- best practices: keyword, vector, hybrid retrieval, reranking, citations, prompt variants
- optional cloud deployment: planned in docs, not part of Attempt 1 runtime validation

## Main Run Commands

```bash
python -m src.ingestion.pipeline --combined-sample
streamlit run app/streamlit_app.py
```

Docker path:

```bash
docker compose up --build
```

## Validation Commands

```bash
python -m src.ingestion.pipeline --combined-sample
python -m src.retrieval.evaluate --sample --top-k 5 --method hybrid_rerank --eval-file data/sample/evaluation_questions_hard.jsonl
python -m src.evaluation.run_answer_evaluation --eval-file data/sample/evaluation_questions_hard.jsonl --top-k 5 --dry-run
python -m src.rag.answer --question "A customer says they were charged twice after upgrading. What should support do?" --top-k 5 --dry-run --prompt-version baseline_grounded
python -m py_compile app/streamlit_app.py app/pages/1_Ask_SupportLens.py app/pages/2_Monitoring_Dashboard.py app/pages/3_Evaluation_Report.py
docker compose config
```

## Known Limitations

- dry-run mode is the default reviewer path
- live Qwen chat validation is blocked by a provider-side quota or billing response
- monitoring is local and file-backed
- the committed Bitext-derived public sample is a subset, not the full public dataset
- Docker packaging is for local reproducibility, not managed deployment

## Final Submission Fields

- GitHub repo URL: `https://github.com/KingsAxe/supportlens-ai-rag`
- commit SHA: `<fill-after-final-commit>`
- FAQ issue URL: `<fill-before-submission>`
- learning-in-public link: `<fill-before-submission>`
- certificate name: `<fill-before-submission>`
