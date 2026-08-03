"""LLM client wrapper with real and deterministic mock modes."""

from __future__ import annotations

import os
import time
from typing import Any

from src.rag.config import RagConfig


def _extract_usage_tokens(response: Any) -> tuple[int | None, int | None]:
    usage = getattr(response, "usage", None)
    if usage is None:
        return None, None
    input_tokens = getattr(usage, "prompt_tokens", None)
    output_tokens = getattr(usage, "completion_tokens", None)
    if input_tokens is None:
        input_tokens = getattr(usage, "input_tokens", None)
    if output_tokens is None:
        output_tokens = getattr(usage, "output_tokens", None)
    return input_tokens, output_tokens


def _build_mock_answer(question: str, citations: list[dict[str, Any]]) -> str:
    if not citations:
        return """## Recommended Response
The available evidence is insufficient to support a grounded recommendation.

## Evidence Used
- None

## Support Notes
Request more account detail or retrieve additional support records before responding."""

    response_lines = [
        "## Recommended Response",
        f"Acknowledge the customer question and anchor the reply in the strongest retrieved evidence {citations[0]['citation_id']}.",
    ]
    if len(citations) > 1:
        response_lines.append(
            f"Use {citations[1]['citation_id']} for supporting policy or workflow context, and avoid making claims beyond the cited evidence."
        )
    response_lines.extend(["", "## Evidence Used"])
    for citation in citations:
        response_lines.append(
            f"- {citation['citation_id']} {citation['source_type']} {citation['source_id']} - {citation['title']}"
        )
    response_lines.extend(
        [
            "",
            "## Support Notes",
            f"This is a deterministic mock answer built from retrieved evidence for the question: {question}",
            "Use the cited records to draft the final customer-facing wording and state clearly if any evidence is insufficient.",
        ]
    )
    return "\n".join(response_lines)


def generate_answer(
    config: RagConfig,
    question: str,
    prompt: str,
    citations: list[dict[str, Any]],
    dry_run: bool = False,
) -> dict[str, Any]:
    if dry_run or not config.real_llm_available:
        started = time.perf_counter()
        answer_text = _build_mock_answer(question, citations)
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        return {
            "answer_text": answer_text,
            "input_tokens": None,
            "output_tokens": None,
            "model": config.model,
            "provider": "mock" if dry_run else config.provider,
            "latency_ms": latency_ms,
            "dry_run": True,
        }

    if not config.openai_available:
        raise RuntimeError("Real LLM mode requested but the 'openai' package is not available.")

    from openai import OpenAI

    client_kwargs: dict[str, Any] = {"api_key": os.getenv("LLM_API_KEY")}
    if config.base_url:
        client_kwargs["base_url"] = config.base_url
    client = OpenAI(**client_kwargs)

    started = time.perf_counter()
    response = client.chat.completions.create(
        model=config.model,
        messages=[
            {"role": "system", "content": "You are a grounded customer support assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
    )
    latency_ms = round((time.perf_counter() - started) * 1000, 2)
    input_tokens, output_tokens = _extract_usage_tokens(response)
    return {
        "answer_text": response.choices[0].message.content or "",
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "model": config.model,
        "provider": config.provider,
        "latency_ms": latency_ms,
        "dry_run": False,
    }