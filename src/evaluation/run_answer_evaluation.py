"""Run dry-run answer evaluation over the sample question sets."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.evaluation.answer_quality import evaluate_answer_quality
from src.ingestion.io import read_jsonl, resolve_repo_path, write_json, write_jsonl
from src.ingestion.schemas import validate_evaluation_questions
from src.rag.answer import run_answer

RESULTS_PATH = resolve_repo_path("data", "processed", "answer_evaluation_results.jsonl")
SUMMARY_PATH = resolve_repo_path("data", "processed", "answer_evaluation_summary.json")


def _average(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def evaluate_answers(
    eval_file: str,
    top_k: int,
    dry_run: bool,
    prompt_version: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    questions = validate_evaluation_questions(read_jsonl(resolve_repo_path(*Path(eval_file).parts)))
    question_dicts = [question.__dict__ for question in questions]

    detailed_results: list[dict[str, Any]] = []
    for question in question_dicts:
        answer_result = run_answer(
            question=question["question"],
            top_k=top_k,
            dry_run=dry_run,
            prompt_version=prompt_version,
        )
        evaluation_result = evaluate_answer_quality(question, answer_result)
        detailed_results.append(evaluation_result)

    summary = {
        "eval_file": eval_file,
        "question_count": len(detailed_results),
        "top_k": top_k,
        "dry_run": dry_run,
        "retrieval_method": "hybrid_rerank",
        "prompt_version": prompt_version,
        "average_source_overlap_rate": round(_average([item["source_overlap_rate"] for item in detailed_results]), 4),
        "average_citation_validity_rate": round(_average([item["citation_validity_rate"] for item in detailed_results]), 4),
        "average_grounding_proxy_score": round(_average([item["grounding_proxy_score"] for item in detailed_results]), 4),
        "basic_quality_pass_rate": round(_average([1.0 if item["passed_basic_quality_checks"] else 0.0 for item in detailed_results]), 4),
        "section_completeness_rate": round(_average([item["section_completeness_rate"] for item in detailed_results]), 4),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return detailed_results, summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run dry-run answer evaluation")
    parser.add_argument("--eval-file", required=True, help="Evaluation question file relative to repo root")
    parser.add_argument("--top-k", type=int, default=5, help="Number of citations to retrieve")
    parser.add_argument("--dry-run", action="store_true", help="Use deterministic mock generation")
    parser.add_argument("--prompt-version", default="baseline_grounded", help="Named prompt variant")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    detailed_results, summary = evaluate_answers(
        eval_file=args.eval_file,
        top_k=args.top_k,
        dry_run=args.dry_run,
        prompt_version=args.prompt_version,
    )
    write_jsonl(RESULTS_PATH, detailed_results)
    write_json(SUMMARY_PATH, summary)
    print("Answer evaluation completed")
    print(f"eval_file={summary['eval_file']}")
    print(f"question_count={summary['question_count']}")
    print(f"top_k={summary['top_k']}")
    print(f"dry_run={summary['dry_run']}")
    print(f"retrieval_method={summary['retrieval_method']}")
    print(f"prompt_version={summary['prompt_version']}")
    print(f"average_source_overlap_rate={summary['average_source_overlap_rate']:.4f}")
    print(f"average_citation_validity_rate={summary['average_citation_validity_rate']:.4f}")
    print(f"average_grounding_proxy_score={summary['average_grounding_proxy_score']:.4f}")
    print(f"basic_quality_pass_rate={summary['basic_quality_pass_rate']:.4f}")
    print(f"section_completeness_rate={summary['section_completeness_rate']:.4f}")


if __name__ == "__main__":
    main()