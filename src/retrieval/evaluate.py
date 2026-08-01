"""Keyword retrieval evaluation for the sample benchmark."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from src.ingestion.io import read_jsonl, resolve_repo_path, write_json
from src.ingestion.pipeline import run_sample_ingestion
from src.ingestion.schemas import validate_evaluation_questions
from src.retrieval.keyword import KeywordRetriever


def ensure_processed_chunks(sample_mode: bool) -> Path:
    processed_chunks = resolve_repo_path("data", "processed", "chunks.jsonl")
    if processed_chunks.exists():
        return processed_chunks
    if not sample_mode:
        raise FileNotFoundError("Missing processed chunks. Run ingestion with --sample first.")
    run_sample_ingestion()
    return processed_chunks


def _expected_ids_for_source_type(question: dict[str, Any], source_type: str) -> set[str]:
    if source_type == "case":
        return set(question["expected_case_ids"])
    if source_type == "policy":
        return set(question["expected_policy_ids"])
    if source_type == "playbook":
        return set(question["expected_playbook_ids"])
    return set()


def evaluate_keyword_retrieval(sample_mode: bool, top_k: int) -> dict[str, Any]:
    chunks_path = ensure_processed_chunks(sample_mode)
    chunks = read_jsonl(chunks_path)
    questions = validate_evaluation_questions(
        read_jsonl(resolve_repo_path("data", "sample", "evaluation_questions.jsonl"))
    )
    question_dicts = [question.__dict__ for question in questions]
    retriever = KeywordRetriever(chunks)

    hit_count = 0
    reciprocal_rank_sum = 0.0
    results_by_question: list[dict[str, Any]] = []

    for question in question_dicts:
        retrieved = retriever.retrieve(question["question"], top_k=top_k)
        hit = 0
        reciprocal_rank = 0.0
        for rank, result in enumerate(retrieved, start=1):
            expected_ids = _expected_ids_for_source_type(question, result["source_type"])
            if result["source_id"] in expected_ids:
                hit = 1
                reciprocal_rank = 1.0 / rank
                break
        hit_count += hit
        reciprocal_rank_sum += reciprocal_rank
        results_by_question.append(
            {
                "question_id": question["question_id"],
                "question": question["question"],
                "hit": bool(hit),
                "reciprocal_rank": reciprocal_rank,
                "retrieved": [
                    {
                        "rank": rank,
                        "chunk_id": item["chunk_id"],
                        "source_type": item["source_type"],
                        "source_id": item["source_id"],
                        "score": item["score"],
                    }
                    for rank, item in enumerate(retrieved, start=1)
                ],
            }
        )

    question_count = len(question_dicts)
    metrics = {
        "retrieval_method": "keyword_bm25_baseline",
        "top_k": top_k,
        "question_count": question_count,
        "hit_rate": hit_count / question_count if question_count else 0.0,
        "mrr": reciprocal_rank_sum / question_count if question_count else 0.0,
        "results_by_question": results_by_question,
    }
    write_json(resolve_repo_path("data", "processed", "keyword_retrieval_metrics.json"), metrics)
    return metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate keyword retrieval on the sample benchmark")
    parser.add_argument("--sample", action="store_true", help="Use the committed sample benchmark")
    parser.add_argument("--top-k", type=int, default=5, help="Number of chunks to retrieve per question")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.sample:
        raise SystemExit("Only --sample is supported in Phase 2.")
    metrics = evaluate_keyword_retrieval(sample_mode=True, top_k=args.top_k)
    print("Keyword retrieval evaluation completed")
    print(f"top_k={metrics['top_k']}")
    print(f"question_count={metrics['question_count']}")
    print(f"hit_rate={metrics['hit_rate']:.4f}")
    print(f"mrr={metrics['mrr']:.4f}")


if __name__ == "__main__":
    main()