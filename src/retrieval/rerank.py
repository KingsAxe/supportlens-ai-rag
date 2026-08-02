"""Lightweight local reranker for hybrid retrieval candidates."""

from __future__ import annotations

from typing import Any

from src.retrieval.keyword import tokenize

Result = dict[str, Any]


def _metadata_text(candidate: Result) -> str:
    metadata = candidate.get("metadata", {})
    parts = [
        candidate.get("source_type", ""),
        metadata.get("title", ""),
        metadata.get("category", ""),
        metadata.get("intent", ""),
        metadata.get("product_area", ""),
        metadata.get("priority", ""),
        metadata.get("status", ""),
    ]
    return " ".join(part for part in parts if part)


def rerank_candidates(query: str, candidates: list[Result], top_k: int = 5) -> list[Result]:
    query_terms = set(tokenize(query))
    if not query_terms:
        return candidates[:top_k]

    scored: list[Result] = []
    max_base = max((float(candidate.get("score", 0.0)) for candidate in candidates), default=1.0) or 1.0
    for candidate in candidates:
        text_terms = set(tokenize(candidate.get("text", "")))
        metadata_terms = set(tokenize(_metadata_text(candidate)))
        lexical_overlap = len(query_terms & text_terms) / len(query_terms)
        metadata_overlap = len(query_terms & metadata_terms) / len(query_terms)
        rank_bonus = 0.0
        if candidate.get("keyword_rank"):
            rank_bonus += 1.0 / float(candidate["keyword_rank"])
        if candidate.get("vector_rank"):
            rank_bonus += 1.0 / float(candidate["vector_rank"])
        base_score = float(candidate.get("score", 0.0)) / max_base
        rerank_score = base_score + 1.1 * lexical_overlap + 0.8 * metadata_overlap + 0.2 * rank_bonus
        scored.append({**candidate, "score": round(rerank_score, 6), "rerank_score": round(rerank_score, 6)})

    selected: list[Result] = []
    remaining = scored[:]
    seen_source_types: set[str] = set()
    while remaining and len(selected) < top_k:
        best_index = 0
        best_score = None
        for index, candidate in enumerate(remaining):
            diversity_bonus = 0.05 if candidate["source_type"] not in seen_source_types else 0.0
            total_score = float(candidate["score"]) + diversity_bonus
            if best_score is None or total_score > best_score:
                best_index = index
                best_score = total_score
        chosen = remaining.pop(best_index)
        seen_source_types.add(chosen["source_type"])
        selected.append(chosen)
    return selected