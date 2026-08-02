"""Hybrid retrieval using reciprocal rank fusion."""

from __future__ import annotations

from typing import Any

Result = dict[str, Any]


def reciprocal_rank_fusion(
    keyword_results: list[Result],
    vector_results: list[Result],
    fusion_k: int = 60,
    top_k: int = 5,
) -> list[Result]:
    fused: dict[str, Result] = {}

    for rank, item in enumerate(keyword_results, start=1):
        fused[item["chunk_id"]] = {
            **item,
            "score": 1.0 / (fusion_k + rank),
            "keyword_rank": rank,
            "vector_rank": None,
        }

    for rank, item in enumerate(vector_results, start=1):
        existing = fused.get(item["chunk_id"])
        if existing is None:
            fused[item["chunk_id"]] = {
                **item,
                "score": 1.0 / (fusion_k + rank),
                "keyword_rank": None,
                "vector_rank": rank,
            }
            continue
        existing["score"] += 1.0 / (fusion_k + rank)
        existing["vector_rank"] = rank

    results = sorted(fused.values(), key=lambda item: item["score"], reverse=True)
    for item in results:
        item["score"] = round(float(item["score"]), 6)
    return results[:top_k]