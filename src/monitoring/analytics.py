"""Monitoring analytics helpers for SupportLens AI."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
from typing import Any

from src.ingestion.io import read_jsonl, resolve_repo_path

MONITORING_EVENTS_PATH = resolve_repo_path("data", "processed", "monitoring_events.jsonl")


def load_monitoring_events() -> list[dict[str, Any]]:
    if not MONITORING_EVENTS_PATH.exists():
        return []
    return read_jsonl(MONITORING_EVENTS_PATH)


def _parse_date(timestamp: str | None) -> str | None:
    if not timestamp:
        return None
    try:
        return datetime.fromisoformat(timestamp).date().isoformat()
    except ValueError:
        return None


def _counter_rows(counter: Counter[str], label_key: str, value_key: str) -> list[dict[str, Any]]:
    return [{label_key: key, value_key: value} for key, value in counter.most_common()]


def summarize_monitoring_events(events: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    if events is None:
        events = load_monitoring_events()

    answer_events = [event for event in events if event.get("event_type") == "answer_generated"]
    feedback_events = [event for event in events if event.get("event_type") == "feedback_submitted"]

    ratings = [event.get("rating") for event in feedback_events if isinstance(event.get("rating"), int)]
    latencies = [event.get("latency_ms") for event in answer_events if isinstance(event.get("latency_ms"), (int, float))]
    thumbs_counter = Counter(str(event.get("thumbs")) for event in feedback_events if event.get("thumbs"))
    mode_counter = Counter(str(event.get("dataset_mode")) for event in events if event.get("dataset_mode"))
    prompt_counter = Counter(str(event.get("prompt_version")) for event in events if event.get("prompt_version"))
    run_mode_counter = Counter("dry-run" if event.get("dry_run", True) else "real-llm" for event in answer_events)
    source_type_counter: Counter[str] = Counter()
    for event in answer_events:
        for source_type in event.get("source_types", []):
            source_type_counter[str(source_type)] += 1

    answer_trend: dict[str, int] = defaultdict(int)
    feedback_trend: dict[str, int] = defaultdict(int)
    for event in answer_events:
        day = _parse_date(event.get("timestamp"))
        if day:
            answer_trend[day] += 1
    for event in feedback_events:
        day = _parse_date(event.get("timestamp"))
        if day:
            feedback_trend[day] += 1

    rating_distribution = Counter(str(rating) for rating in ratings)

    return {
        "total_questions": len(answer_events),
        "total_feedback_submissions": len(feedback_events),
        "average_rating": round(sum(ratings) / len(ratings), 4) if ratings else None,
        "thumbs_up_count": thumbs_counter.get("up", 0),
        "thumbs_down_count": thumbs_counter.get("down", 0),
        "average_latency_ms": round(sum(latencies) / len(latencies), 4) if latencies else None,
        "dry_run_vs_real": _counter_rows(run_mode_counter, "mode", "count"),
        "most_common_source_types": _counter_rows(source_type_counter, "source_type", "count"),
        "most_common_dataset_modes": _counter_rows(mode_counter, "dataset_mode", "count"),
        "top_prompt_versions": _counter_rows(prompt_counter, "prompt_version", "count"),
        "answer_trend": [{"date": day, "count": count} for day, count in sorted(answer_trend.items())],
        "feedback_trend": [{"date": day, "count": count} for day, count in sorted(feedback_trend.items())],
        "rating_distribution": [{"rating": rating, "count": count} for rating, count in sorted(rating_distribution.items())],
        "latency_distribution": [{"latency_ms": value} for value in latencies],
    }
