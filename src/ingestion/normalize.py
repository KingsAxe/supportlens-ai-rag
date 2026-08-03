"""Normalization of source records into shared retrieval documents."""

from __future__ import annotations

from typing import Any

from src.ingestion.schemas import ResolutionPlaybook, SupportCase, SupportPolicy

Document = dict[str, Any]


def normalize_support_case(record: SupportCase) -> Document:
    title = f"Support case {record.case_id}: {record.intent.replace('_', ' ')}"
    content = "\n".join(
        [
            f"Customer message: {record.customer_message}",
            f"Resolution summary: {record.resolution_summary}",
            f"Agent response: {record.agent_response}",
        ]
    )
    return {
        'document_id': f'doc-case-{record.case_id}',
        'source_type': 'case',
        'source_id': record.case_id,
        'title': title,
        'category': record.category,
        'content': content,
        'metadata': {
            'case_id': record.case_id,
            'intent': record.intent,
            'product_area': record.product_area,
            'priority': record.priority,
            'status': record.status,
            'created_at': record.created_at,
            'provenance': 'public_sample' if record.source_dataset else 'synthetic_sample',
            'source_dataset': record.source_dataset,
            'source_license': record.source_license,
            'source_record_id': record.source_record_id,
        },
    }


def normalize_support_policy(record: SupportPolicy) -> Document:
    return {
        'document_id': f'doc-policy-{record.policy_id}',
        'source_type': 'policy',
        'source_id': record.policy_id,
        'title': record.title,
        'category': record.category,
        'content': record.policy_text,
        'metadata': {
            'policy_id': record.policy_id,
            'effective_date': record.effective_date,
            'source_label': record.source_type,
        },
    }


def normalize_resolution_playbook(record: ResolutionPlaybook) -> Document:
    content = "\n\n".join(
        [
            f"Trigger conditions: {record.trigger_conditions}",
            f"Recommended steps: {record.recommended_steps}",
            f"Escalation rules: {record.escalation_rules}",
        ]
    )
    return {
        'document_id': f'doc-playbook-{record.playbook_id}',
        'source_type': 'playbook',
        'source_id': record.playbook_id,
        'title': record.title,
        'category': record.category,
        'content': content,
        'metadata': {
            'playbook_id': record.playbook_id,
            'trigger_conditions': record.trigger_conditions,
            'source_label': record.source_type,
        },
    }


def normalize_all(
    support_cases: list[SupportCase],
    support_policies: list[SupportPolicy],
    resolution_playbooks: list[ResolutionPlaybook],
) -> list[Document]:
    documents: list[Document] = []
    documents.extend(normalize_support_case(record) for record in support_cases)
    documents.extend(normalize_support_policy(record) for record in support_policies)
    documents.extend(normalize_resolution_playbook(record) for record in resolution_playbooks)
    return documents
