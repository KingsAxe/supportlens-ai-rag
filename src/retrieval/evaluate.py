"""Comparative retrieval evaluation for the sample benchmark."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.ingestion.io import read_jsonl, resolve_repo_path, write_json
from src.ingestion.pipeline import run_sample_ingestion
from src.ingestion.schemas import validate_evaluation_questions
from src.retrieval.hybrid import reciprocal_rank_fusion
from src.retrieval.keyword import KeywordRetriever
from src.retrieval.rerank import rerank_candidates
from src.retrieval.vector import DEFAULT_MODEL_NAME, VectorRetriever

METHODS = ("keyword", "vector", "hybrid", "hybrid_rerank")


def ensure_processed_chunks(sample_mode: bool) -> Path:
    processed_chunks = resolve_repo_path("data", "processed", "chunks.jsonl")
    if processed_chunks.exists():
        return processed_chunks
    if not sample_mode:
        raise FileNotFoundError("Missing processed chunks. Run ingestion with --sample first.")
    run_sample_ingestion()
    return processed_chunks


def _source_id_sets() -> tuple[set[str], set[str], set[str]]:
    support_cases = read_jsonl(resolve_repo_path("data", "sample", "support_cases.jsonl"))
    support_policies = read_jsonl(resolve_repo_path("data", "sample", "support_policies.jsonl"))
    playbooks = read_jsonl(resolve_repo_path("data", "sample", "resolution_playbooks.jsonl"))
    return (
        {record["case_id"] for record in support_cases},
        {record["policy_id"] for record in support_policies},
        {record["playbook_id"] for record in playbooks},
    )


def _validate_question_references(question_dicts: list[dict[str, Any]]) -> None:
    case_ids, policy_ids, playbook_ids = _source_id_sets()
    for question in question_dicts:
        for case_id in question["expected_case_ids"]:
            if case_id not in case_ids:
                raise ValueError(f"Question {question['question_id']} references unknown case id {case_id}")
        for policy_id in question["expected_policy_ids"]:
            if policy_id not in policy_ids:
                raise ValueError(f"Question {question['question_id']} references unknown policy id {policy_id}")
        for playbook_id in question["expected_playbook_ids"]:
            if playbook_id not in playbook_ids:
                raise ValueError(f"Question {question['question_id']} references unknown playbook id {playbook_id}")


def _expected_ids_for_source_type(question: dict[str, Any], source_type: str) -> set[str]:
    if source_type == "case":
        return set(question["expected_case_ids"])
    if source_type == "policy":
        return set(question["expected_policy_ids"])
    if source_type == "playbook":
        return set(question["expected_playbook_ids"])
    return set()


def _evaluate_results(question_dicts: list[dict[str, Any]], method: str, top_k: int, query_fn) -> dict[str, Any]:
    hit_count = 0
    reciprocal_rank_sum = 0.0
    results_by_question: list[dict[str, Any]] = []

    for question in question_dicts:
        retrieved = query_fn(question["question"], top_k)
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
                "difficulty": question.get("difficulty"),
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
    return {
        "retrieval_method": method,
        "top_k": top_k,
        "question_count": question_count,
        "hit_rate": hit_count / question_count if question_count else 0.0,
        "mrr": reciprocal_rank_sum / question_count if question_count else 0.0,
        "results_by_question": results_by_question,
    }


def _method_output_path(method: str) -> Path:
    return resolve_repo_path("data", "processed", f"{method}_retrieval_metrics.json")


def evaluate_retrieval(
    sample_mode: bool,
    method: str,
    top_k: int,
    eval_file: str,
    model_name: str = DEFAULT_MODEL_NAME,
) -> dict[str, Any]:
    chunks_path = ensure_processed_chunks(sample_mode)
    chunks = read_jsonl(chunks_path)
    questions = validate_evaluation_questions(read_jsonl(resolve_repo_path(*Path(eval_file).parts)))
    question_dicts = [question.__dict__ for question in questions]
    _validate_question_references(question_dicts)

    keyword_retriever = KeywordRetriever(chunks)
    vector_retriever = VectorRetriever(chunks=chunks, model_name=model_name)
    candidate_pool = max(top_k * 3, 10)

    evaluators = {
        "keyword": lambda query, requested_top_k: keyword_retriever.retrieve(query, top_k=requested_top_k),
        "vector": lambda query, requested_top_k: vector_retriever.retrieve(query, top_k=requested_top_k),
        "hybrid": lambda query, requested_top_k: reciprocal_rank_fusion(
            keyword_retriever.retrieve(query, top_k=candidate_pool),
            vector_retriever.retrieve(query, top_k=candidate_pool),
            top_k=requested_top_k,
        ),
        "hybrid_rerank": lambda query, requested_top_k: rerank_candidates(
            query,
            reciprocal_rank_fusion(
                keyword_retriever.retrieve(query, top_k=candidate_pool),
                vector_retriever.retrieve(query, top_k=candidate_pool),
                top_k=candidate_pool,
            ),
            top_k=requested_top_k,
        ),
    }

    if method == "all":
        comparison = {
            "eval_file": eval_file,
            "top_k": top_k,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "methods": {},
        }
        for method_name in METHODS:
            metrics = _evaluate_results(question_dicts, method_name, top_k, evaluators[method_name])
            metrics["eval_file"] = eval_file
            comparison["methods"][method_name] = {
                "hit_rate": metrics["hit_rate"],
                "mrr": metrics["mrr"],
                "question_count": metrics["question_count"],
                "top_k": top_k,
                "eval_file": eval_file,
                "timestamp": comparison["timestamp"],
            }
            write_json(_method_output_path(method_name), metrics)
        write_json(resolve_repo_path("data", "processed", "retrieval_comparison_metrics.json"), comparison)
        return comparison

    if method not in evaluators:
        raise ValueError(f"Unsupported retrieval method: {method}")

    metrics = _evaluate_results(question_dicts, method, top_k, evaluators[method])
    metrics["eval_file"] = eval_file
    metrics["timestamp"] = datetime.now(timezone.utc).isoformat()
    write_json(_method_output_path(method), metrics)
    return metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate retrieval on the sample benchmark")
    parser.add_argument("--sample", action="store_true", help="Use the committed sample benchmark")
    parser.add_argument("--top-k", type=int, default=5, help="Number of chunks to retrieve per question")
    parser.add_argument("--method", default="keyword", help="keyword, vector, hybrid, hybrid_rerank, or all")
    parser.add_argument(
        "--eval-file",
        default="data/sample/evaluation_questions.jsonl",
        help="Path to the evaluation question JSONL file relative to the repository root",
    )
    parser.add_argument(
        "--embedding-model",
        default=DEFAULT_MODEL_NAME,
        help="Embedding model name for sentence-transformers when available",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.sample:
        raise SystemExit("Only --sample is supported in Phase 3.")
    metrics = evaluate_retrieval(
        sample_mode=True,
        method=args.method,
        top_k=args.top_k,
        eval_file=args.eval_file,
        model_name=args.embedding_model,
    )
    if args.method == "all":
        print("Retrieval comparison completed")
        for method_name in METHODS:
            summary = metrics["methods"][method_name]
            print(
                f"{method_name}: hit_rate={summary['hit_rate']:.4f} "
                f"mrr={summary['mrr']:.4f} questions={summary['question_count']}"
            )
        return
    print("Retrieval evaluation completed")
    print(f"method={metrics['retrieval_method']}")
    print(f"top_k={metrics['top_k']}")
    print(f"question_count={metrics['question_count']}")
    print(f"hit_rate={metrics['hit_rate']:.4f}")
    print(f"mrr={metrics['mrr']:.4f}")


if __name__ == "__main__":
    main()