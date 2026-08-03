"""Lightweight answer evaluation hooks for later phases."""

from __future__ import annotations

import re
from typing import Any

_CITATION_RE = re.compile(r"\[C\d+\]")


def extract_citation_ids(answer_text: str) -> list[str]:
    return _CITATION_RE.findall(answer_text)


def check_answer_citations(answer_text: str, valid_citation_ids: list[str]) -> dict[str, Any]:
    found = extract_citation_ids(answer_text)
    valid_set = set(valid_citation_ids)
    unsupported = sorted({citation for citation in found if citation not in valid_set})
    return {
        "contains_citations": bool(found),
        "found_citation_ids": found,
        "valid_citation_ids": valid_citation_ids,
        "unsupported_citation_ids": unsupported,
        "all_citations_valid": not unsupported,
    }


def check_expected_source_overlap(retrieved_source_ids: list[str], expected_source_ids: list[str]) -> dict[str, Any]:
    overlap = sorted(set(retrieved_source_ids) & set(expected_source_ids))
    return {
        "retrieved_source_ids": retrieved_source_ids,
        "expected_source_ids": expected_source_ids,
        "overlap_source_ids": overlap,
        "has_expected_overlap": bool(overlap),
    }


def summarize_answer_shape(answer_text: str, evidence_count: int) -> dict[str, Any]:
    return {
        "answer_length_chars": len(answer_text),
        "answer_length_words": len(answer_text.split()),
        "evidence_count": evidence_count,
    }