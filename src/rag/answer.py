"""CLI entrypoint for grounded answer generation."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.ingestion.io import append_jsonl, read_jsonl, resolve_repo_path
from src.ingestion.pipeline import run_sample_ingestion
from src.rag.citations import build_citations
from src.rag.config import load_config
from src.rag.evaluation_hooks import check_answer_citations, summarize_answer_shape
from src.rag.llm_client import generate_answer
from src.rag.prompts import PROMPT_VARIANTS, build_answer_prompt
from src.retrieval.hybrid import reciprocal_rank_fusion
from src.retrieval.keyword import KeywordRetriever, tokenize
from src.retrieval.rerank import rerank_candidates
from src.retrieval.vector import DEFAULT_MODEL_NAME, VectorRetriever


RAG_RUNS_PATH = resolve_repo_path("data", "processed", "rag_runs.jsonl")


def ensure_processed_chunks() -> Path:
    chunks_path = resolve_repo_path("data", "processed", "chunks.jsonl")
    if chunks_path.exists():
        return chunks_path
    run_sample_ingestion()
    return chunks_path


def _select_citation_subset(question: str, candidates: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
    query_terms = set(tokenize(question))
    rescored: list[dict[str, Any]] = []
    total_candidates = max(len(candidates), 1)
    for rank, candidate in enumerate(candidates, start=1):
        text_terms = set(tokenize(candidate.get("text", "")))
        metadata = candidate.get("metadata", {})
        metadata_terms = set(
            tokenize(" ".join(str(metadata.get(key, "")) for key in ("title", "category", "intent", "product_area")))
        )
        overlap = len(query_terms & (text_terms | metadata_terms)) / max(len(query_terms), 1)
        rank_component = 1.0 - ((rank - 1) / total_candidates)
        source_bonus = 0.12 if candidate["source_type"] in {"policy", "playbook"} else 0.0
        answer_score = 2.0 * overlap + 0.4 * rank_component + source_bonus
        rescored.append({**candidate, "answer_score": round(answer_score, 6)})

    rescored.sort(key=lambda item: item["answer_score"], reverse=True)
    selected: list[dict[str, Any]] = []
    seen_types: set[str] = set()
    for candidate in rescored:
        if len(selected) >= top_k:
            break
        if candidate["source_type"] not in seen_types or len(seen_types) >= 3:
            selected.append(candidate)
            seen_types.add(candidate["source_type"])
    if len(selected) < top_k:
        for candidate in rescored:
            if candidate in selected:
                continue
            selected.append(candidate)
            if len(selected) >= top_k:
                break
    return selected[:top_k]


def retrieve_hybrid_rerank(question: str, top_k: int, embedding_model: str = DEFAULT_MODEL_NAME) -> list[dict[str, Any]]:
    chunks = read_jsonl(ensure_processed_chunks())
    keyword = KeywordRetriever(chunks)
    vector = VectorRetriever(chunks=chunks, model_name=embedding_model)
    candidate_pool = max(top_k * 4, 12)
    fused = reciprocal_rank_fusion(
        keyword.retrieve(question, top_k=candidate_pool),
        vector.retrieve(question, top_k=candidate_pool),
        top_k=candidate_pool,
    )
    reranked = rerank_candidates(question, fused, top_k=candidate_pool)
    return _select_citation_subset(question, reranked, top_k=top_k)


def run_answer(
    question: str,
    top_k: int,
    dry_run: bool,
    embedding_model: str = DEFAULT_MODEL_NAME,
    prompt_version: str = "baseline_grounded",
) -> dict[str, Any]:
    config = load_config()
    retrieval_results = retrieve_hybrid_rerank(question=question, top_k=top_k, embedding_model=embedding_model)
    citations = build_citations(retrieval_results)
    prompt = build_answer_prompt(question=question, citations=citations, prompt_version=prompt_version)
    llm_output = generate_answer(
        config=config,
        question=question,
        prompt=prompt,
        citations=citations,
        dry_run=dry_run,
    )
    citation_check = check_answer_citations(llm_output["answer_text"], [item["citation_id"] for item in citations])
    shape_summary = summarize_answer_shape(llm_output["answer_text"], len(citations))

    run_metadata = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "question": question,
        "retrieval_method": "hybrid_rerank",
        "top_k": top_k,
        "citation_ids": [item["citation_id"] for item in citations],
        "source_ids": [item["source_id"] for item in citations],
        "provider": llm_output["provider"],
        "model": llm_output["model"],
        "latency_ms": llm_output["latency_ms"],
        "input_tokens": llm_output["input_tokens"],
        "output_tokens": llm_output["output_tokens"],
        "dry_run": llm_output["dry_run"],
        "prompt_version": prompt_version,
    }
    append_jsonl(RAG_RUNS_PATH, run_metadata)

    return {
        "question": question,
        "retrieval_method": "hybrid_rerank",
        "citations": citations,
        "retrieved_evidence": retrieval_results,
        "prompt": prompt,
        "prompt_version": prompt_version,
        "answer_text": llm_output["answer_text"],
        "provider": llm_output["provider"],
        "model": llm_output["model"],
        "latency_ms": llm_output["latency_ms"],
        "input_tokens": llm_output["input_tokens"],
        "output_tokens": llm_output["output_tokens"],
        "dry_run": llm_output["dry_run"],
        "evaluation_hooks": {
            **citation_check,
            **shape_summary,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a grounded support answer")
    parser.add_argument("--question", required=True, help="Support question to answer")
    parser.add_argument("--top-k", type=int, default=5, help="Number of citations to retrieve")
    parser.add_argument("--dry-run", action="store_true", help="Use deterministic mock generation")
    parser.add_argument(
        "--embedding-model",
        default=DEFAULT_MODEL_NAME,
        help="Embedding model name for vector retrieval when available",
    )
    parser.add_argument(
        "--prompt-version",
        default="baseline_grounded",
        choices=sorted(PROMPT_VARIANTS),
        help="Named prompt variant for answer generation",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_answer(
        question=args.question,
        top_k=args.top_k,
        dry_run=args.dry_run,
        embedding_model=args.embedding_model,
        prompt_version=args.prompt_version,
    )
    print(result["answer_text"])
    print("\nCitations:")
    for citation in result["citations"]:
        print(f"- {citation['citation_id']} {citation['source_type']} {citation['source_id']} | {citation['title']}")
    print("\nRun Metadata:")
    print(f"provider={result['provider']}")
    print(f"model={result['model']}")
    print(f"retrieval_method={result['retrieval_method']}")
    print(f"prompt_version={result['prompt_version']}")
    print(f"latency_ms={result['latency_ms']}")
    print(f"dry_run={result['dry_run']}")


if __name__ == "__main__":
    main()