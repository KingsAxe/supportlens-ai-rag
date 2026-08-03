"""Transparent non-LLM quality checks for generated answers."""

from __future__ import annotations

from typing import Any

from src.rag.evaluation_hooks import check_answer_citations, check_expected_source_overlap, extract_citation_ids

REQUIRED_SECTIONS = (
    "## Recommended Response",
    "## Evidence Used",
    "## Support Notes",
)
MIN_ANSWER_WORDS = 20
MAX_ANSWER_WORDS = 220
MIN_EVIDENCE_COUNT = 2


def _rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def evaluate_answer_quality(
    question_record: dict[str, Any],
    answer_result: dict[str, Any],
) -> dict[str, Any]:
    answer_text = answer_result["answer_text"]
    citations = answer_result["citations"]
    citation_ids = [item["citation_id"] for item in citations]
    citation_check = check_answer_citations(answer_text, citation_ids)
    retrieved_source_ids = [item["source_id"] for item in citations]
    expected_source_ids = (
        list(question_record.get("expected_case_ids", []))
        + list(question_record.get("expected_policy_ids", []))
        + list(question_record.get("expected_playbook_ids", []))
    )
    overlap_check = check_expected_source_overlap(retrieved_source_ids, expected_source_ids)

    answer_words = len(answer_text.split())
    has_sections = {section: (section in answer_text) for section in REQUIRED_SECTIONS}
    section_hits = sum(1 for present in has_sections.values() if present)
    valid_found_citations = [cid for cid in citation_check["found_citation_ids"] if cid in citation_ids]

    citation_validity_rate = _rate(len(valid_found_citations), len(citation_check["found_citation_ids"]))
    source_overlap_rate = _rate(len(overlap_check["overlap_source_ids"]), len(set(expected_source_ids)))
    section_completeness_rate = _rate(section_hits, len(REQUIRED_SECTIONS))
    insufficient_evidence_flag = len(citations) < MIN_EVIDENCE_COUNT
    excessive_answer_length_flag = answer_words > MAX_ANSWER_WORDS
    minimum_answer_length_ok = answer_words >= MIN_ANSWER_WORDS

    grounding_proxy_score = round(
        (citation_validity_rate + source_overlap_rate + section_completeness_rate) / 3,
        4,
    )

    passed_basic_quality_checks = all(
        [
            citation_check["contains_citations"],
            citation_check["all_citations_valid"],
            minimum_answer_length_ok,
            section_hits == len(REQUIRED_SECTIONS),
            not insufficient_evidence_flag,
        ]
    )

    return {
        "question_id": question_record["question_id"],
        "question": question_record["question"],
        "answer_type": question_record["answer_type"],
        "difficulty": question_record.get("difficulty"),
        "expected_source_ids": expected_source_ids,
        "retrieved_source_ids": retrieved_source_ids,
        "citation_ids": extract_citation_ids(answer_text),
        "valid_citation_ids": citation_ids,
        "unsupported_citation_ids": citation_check["unsupported_citation_ids"],
        "has_recommended_response": has_sections["## Recommended Response"],
        "has_evidence_used": has_sections["## Evidence Used"],
        "has_support_notes": has_sections["## Support Notes"],
        "answer_length": answer_words,
        "evidence_count": len(citations),
        "source_overlap_count": len(overlap_check["overlap_source_ids"]),
        "source_overlap_rate": round(source_overlap_rate, 4),
        "citation_validity_rate": round(citation_validity_rate, 4),
        "grounding_proxy_score": grounding_proxy_score,
        "minimum_answer_length_ok": minimum_answer_length_ok,
        "excessive_answer_length_flag": excessive_answer_length_flag,
        "insufficient_evidence_flag": insufficient_evidence_flag,
        "passed_basic_quality_checks": passed_basic_quality_checks,
        "section_completeness_rate": round(section_completeness_rate, 4),
        "prompt_version": answer_result["prompt_version"],
        "retrieval_method": answer_result["retrieval_method"],
        "dry_run": answer_result["dry_run"],
        "provider": answer_result["provider"],
        "model": answer_result["model"],
    }