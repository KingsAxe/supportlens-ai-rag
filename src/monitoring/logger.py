"""Local JSONL monitoring logger for SupportLens AI."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from src.ingestion.io import append_jsonl, resolve_repo_path, write_jsonl

MONITORING_EVENTS_PATH = resolve_repo_path("data", "processed", "monitoring_events.jsonl")


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _coerce_string_list(values: list[Any]) -> list[str]:
    return [str(value) for value in values if value is not None]


def log_answer_generated(result: dict[str, Any], question: str, top_k: int) -> dict[str, Any]:
    citations = result.get("citations", [])
    event = {
        "timestamp": _utc_timestamp(),
        "event_type": "answer_generated",
        "question": question,
        "dataset_mode": result.get("dataset_mode"),
        "retrieval_method": result.get("retrieval_method"),
        "top_k": top_k,
        "prompt_version": result.get("prompt_version"),
        "dry_run": bool(result.get("dry_run", True)),
        "provider": result.get("provider"),
        "model": result.get("model"),
        "latency_ms": result.get("latency_ms"),
        "citation_count": len(citations),
        "source_ids": _coerce_string_list([item.get("source_id") for item in citations]),
        "source_types": _coerce_string_list([item.get("source_type") for item in citations]),
    }
    append_jsonl(MONITORING_EVENTS_PATH, event)
    return event


def log_feedback_submitted(
    result: dict[str, Any],
    question: str,
    top_k: int,
    rating: int,
    thumbs: str,
    feedback_text: str,
) -> dict[str, Any]:
    citations = result.get("citations", [])
    event = {
        "timestamp": _utc_timestamp(),
        "event_type": "feedback_submitted",
        "question": question,
        "rating": int(rating),
        "thumbs": thumbs,
        "feedback_text": feedback_text.strip(),
        "dataset_mode": result.get("dataset_mode"),
        "retrieval_method": result.get("retrieval_method"),
        "top_k": top_k,
        "prompt_version": result.get("prompt_version"),
        "dry_run": bool(result.get("dry_run", True)),
        "citation_count": len(citations),
        "source_ids": _coerce_string_list([item.get("source_id") for item in citations]),
    }
    append_jsonl(MONITORING_EVENTS_PATH, event)
    return event


def create_demo_monitoring_events() -> list[dict[str, Any]]:
    base_time = datetime(2026, 8, 3, 9, 0, tzinfo=timezone.utc)
    demo_events: list[dict[str, Any]] = [
        {
            "timestamp": (base_time + timedelta(minutes=0)).isoformat(),
            "event_type": "answer_generated",
            "question": "A customer wants a refund after a failed payment.",
            "dataset_mode": "combined_sample",
            "retrieval_method": "hybrid_rerank",
            "top_k": 5,
            "prompt_version": "baseline_grounded",
            "dry_run": True,
            "provider": "mock",
            "model": "mock-supportlens",
            "latency_ms": 12.4,
            "citation_count": 5,
            "source_ids": ["CASE-011", "POL-003", "PB-006"],
            "source_types": ["case", "policy", "playbook"],
            "demo_data": True,
        },
        {
            "timestamp": (base_time + timedelta(minutes=2)).isoformat(),
            "event_type": "feedback_submitted",
            "question": "A customer wants a refund after a failed payment.",
            "rating": 5,
            "thumbs": "up",
            "feedback_text": "Helpful refund and retry guidance.",
            "dataset_mode": "combined_sample",
            "retrieval_method": "hybrid_rerank",
            "top_k": 5,
            "prompt_version": "baseline_grounded",
            "dry_run": True,
            "citation_count": 5,
            "source_ids": ["CASE-011", "POL-003", "PB-006"],
            "demo_data": True,
        },
        {
            "timestamp": (base_time + timedelta(minutes=15)).isoformat(),
            "event_type": "answer_generated",
            "question": "The account owner cannot access the workspace after repeated login failures.",
            "dataset_mode": "combined_sample",
            "retrieval_method": "hybrid_rerank",
            "top_k": 5,
            "prompt_version": "policy_first",
            "dry_run": True,
            "provider": "mock",
            "model": "mock-supportlens",
            "latency_ms": 18.1,
            "citation_count": 4,
            "source_ids": ["CASE-003", "POL-004", "PB-005"],
            "source_types": ["case", "policy", "playbook"],
            "demo_data": True,
        },
        {
            "timestamp": (base_time + timedelta(minutes=18)).isoformat(),
            "event_type": "feedback_submitted",
            "question": "The account owner cannot access the workspace after repeated login failures.",
            "rating": 4,
            "thumbs": "up",
            "feedback_text": "Good account recovery structure.",
            "dataset_mode": "combined_sample",
            "retrieval_method": "hybrid_rerank",
            "top_k": 5,
            "prompt_version": "policy_first",
            "dry_run": True,
            "citation_count": 4,
            "source_ids": ["CASE-003", "POL-004", "PB-005"],
            "demo_data": True,
        },
        {
            "timestamp": (base_time + timedelta(minutes=32)).isoformat(),
            "event_type": "answer_generated",
            "question": "A customer was charged twice after upgrading and wants the duplicate reversed.",
            "dataset_mode": "sample",
            "retrieval_method": "hybrid_rerank",
            "top_k": 5,
            "prompt_version": "concise_support",
            "dry_run": True,
            "provider": "mock",
            "model": "mock-supportlens",
            "latency_ms": 15.9,
            "citation_count": 5,
            "source_ids": ["CASE-017", "POL-001", "PB-001"],
            "source_types": ["case", "policy", "playbook"],
            "demo_data": True,
        },
        {
            "timestamp": (base_time + timedelta(minutes=36)).isoformat(),
            "event_type": "feedback_submitted",
            "question": "A customer was charged twice after upgrading and wants the duplicate reversed.",
            "rating": 3,
            "thumbs": "down",
            "feedback_text": "Needed a clearer customer-facing explanation.",
            "dataset_mode": "sample",
            "retrieval_method": "hybrid_rerank",
            "top_k": 5,
            "prompt_version": "concise_support",
            "dry_run": True,
            "citation_count": 5,
            "source_ids": ["CASE-017", "POL-001", "PB-001"],
            "demo_data": True,
        },
    ]
    write_jsonl(MONITORING_EVENTS_PATH, demo_events)
    return demo_events
