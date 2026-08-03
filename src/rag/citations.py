"""Citation packaging for retrieved evidence."""

from __future__ import annotations

from typing import Any

EvidenceItem = dict[str, Any]


def build_citations(results: list[dict[str, Any]]) -> list[EvidenceItem]:
    citations: list[EvidenceItem] = []
    for index, result in enumerate(results, start=1):
        metadata = result.get("metadata", {})
        citations.append(
            {
                "citation_id": f"[C{index}]",
                "source_type": result["source_type"],
                "source_id": result["source_id"],
                "title": metadata.get("title", f"{result['source_type']} {result['source_id']}"),
                "category": metadata.get("category", "unknown"),
                "text": result["text"],
                "metadata": metadata,
                "score": result["score"],
            }
        )
    return citations