"""Sample ingestion pipeline for SupportLens AI."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.ingestion.chunking import chunk_documents
from src.ingestion.io import read_jsonl, resolve_repo_path, write_json, write_jsonl
from src.ingestion.normalize import normalize_all
from src.ingestion.schemas import (
    serialize_dataclasses,
    validate_evaluation_questions,
    validate_resolution_playbooks,
    validate_support_cases,
    validate_support_policies,
)


SAMPLE_INPUTS = {
    "support_cases": "support_cases.jsonl",
    "support_policies": "support_policies.jsonl",
    "resolution_playbooks": "resolution_playbooks.jsonl",
    "evaluation_questions": "evaluation_questions.jsonl",
}


def run_sample_ingestion() -> dict[str, Any]:
    sample_dir = resolve_repo_path("data", "sample")
    processed_dir = resolve_repo_path("data", "processed")

    support_cases = validate_support_cases(read_jsonl(sample_dir / SAMPLE_INPUTS["support_cases"]))
    support_policies = validate_support_policies(read_jsonl(sample_dir / SAMPLE_INPUTS["support_policies"]))
    resolution_playbooks = validate_resolution_playbooks(
        read_jsonl(sample_dir / SAMPLE_INPUTS["resolution_playbooks"])
    )
    evaluation_questions = validate_evaluation_questions(
        read_jsonl(sample_dir / SAMPLE_INPUTS["evaluation_questions"])
    )

    documents = normalize_all(support_cases, support_policies, resolution_playbooks)
    chunks = chunk_documents(documents)

    write_jsonl(processed_dir / "documents.jsonl", documents)
    write_jsonl(processed_dir / "chunks.jsonl", chunks)

    summary = {
        "support_case_count": len(support_cases),
        "policy_count": len(support_policies),
        "playbook_count": len(resolution_playbooks),
        "evaluation_question_count": len(evaluation_questions),
        "document_count": len(documents),
        "chunk_count": len(chunks),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "validation_status": "passed",
    }
    write_json(processed_dir / "ingestion_summary.json", summary)

    return {
        "support_cases": serialize_dataclasses(support_cases),
        "support_policies": serialize_dataclasses(support_policies),
        "resolution_playbooks": serialize_dataclasses(resolution_playbooks),
        "evaluation_questions": serialize_dataclasses(evaluation_questions),
        "documents": documents,
        "chunks": chunks,
        "summary": summary,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the SupportLens AI ingestion pipeline")
    parser.add_argument("--sample", action="store_true", help="Process the committed sample dataset")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.sample:
        raise SystemExit("Only --sample is supported in Phase 2.")

    result = run_sample_ingestion()
    summary = result["summary"]
    print("Ingestion completed")
    print(f"support_cases={summary['support_case_count']}")
    print(f"policies={summary['policy_count']}")
    print(f"playbooks={summary['playbook_count']}")
    print(f"documents={summary['document_count']}")
    print(f"chunks={summary['chunk_count']}")
    print(f"validation_status={summary['validation_status']}")


if __name__ == "__main__":
    main()