"""Prompt builders for grounded support response generation."""

from __future__ import annotations

from typing import Any

PROMPT_VARIANTS: dict[str, str] = {
    "baseline_grounded": """You are SupportLens AI, a grounded customer-support assistant.

Answer the support question using only the provided evidence.
Rules:
- Do not invent policy details or workflow steps.
- Cite factual claims using the provided citation IDs like [C1] and [C2].
- If the evidence is insufficient, say that clearly.
- Separate the customer-facing response from internal support notes.
- Keep a professional and practical support tone.""",
    "concise_support": """You are SupportLens AI, a grounded customer-support assistant.

Answer the support question using only the provided evidence.
Rules:
- Be concise and practical.
- Cite factual claims using the provided citation IDs like [C1] and [C2].
- If the evidence is insufficient, say that clearly.
- Do not invent policy details or workflow steps.
- Separate the customer-facing response from internal support notes.""",
    "policy_first": """You are SupportLens AI, a grounded customer-support assistant.

Answer the support question using only the provided evidence.
Rules:
- Prioritize policy-backed guidance before procedural suggestions.
- Cite factual claims using the provided citation IDs like [C1] and [C2].
- If the evidence is insufficient, say that clearly.
- Do not invent policy details or workflow steps.
- Separate the customer-facing response from internal support notes.""",
}


def render_evidence_block(citations: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for citation in citations:
        lines.append(
            "\n".join(
                [
                    f"{citation['citation_id']} | {citation['source_type']} | {citation['source_id']} | {citation['title']} | {citation['category']}",
                    citation["text"],
                ]
            )
        )
    return "\n\n".join(lines)


def get_prompt_variant(prompt_version: str) -> str:
    if prompt_version not in PROMPT_VARIANTS:
        valid = ", ".join(sorted(PROMPT_VARIANTS))
        raise ValueError(f"Unknown prompt version '{prompt_version}'. Valid options: {valid}")
    return PROMPT_VARIANTS[prompt_version]


def build_answer_prompt(
    question: str,
    citations: list[dict[str, Any]],
    prompt_version: str = "baseline_grounded",
) -> str:
    prompt_preamble = get_prompt_variant(prompt_version)
    evidence_block = render_evidence_block(citations)
    return f"""{prompt_preamble}

Output exactly in this markdown structure:
## Recommended Response
...

## Evidence Used
- [C1] ...
- [C2] ...

## Support Notes
...

Support question:
{question}

Evidence:
{evidence_block}
"""