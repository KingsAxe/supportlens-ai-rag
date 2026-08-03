"""Lightweight schema validation for sample ingestion data."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from typing import Any


@dataclass(frozen=True)
class SupportCase:
    case_id: str
    customer_message: str
    category: str
    intent: str
    product_area: str
    priority: str
    status: str
    resolution_summary: str
    agent_response: str
    created_at: str
    source_dataset: str | None = None
    source_license: str | None = None
    source_record_id: str | None = None


@dataclass(frozen=True)
class SupportPolicy:
    policy_id: str
    title: str
    category: str
    policy_text: str
    effective_date: str
    source_type: str


@dataclass(frozen=True)
class ResolutionPlaybook:
    playbook_id: str
    title: str
    category: str
    trigger_conditions: str
    recommended_steps: str
    escalation_rules: str
    source_type: str


@dataclass(frozen=True)
class EvaluationQuestion:
    question_id: str
    question: str
    expected_case_ids: list[str]
    expected_policy_ids: list[str]
    expected_playbook_ids: list[str]
    answer_type: str
    difficulty: str | None = None
    notes: str = ""


REQUIRED_FIELDS: dict[str, tuple[str, ...]] = {
    'support_case': (
        'case_id',
        'customer_message',
        'category',
        'intent',
        'product_area',
        'priority',
        'status',
        'resolution_summary',
        'agent_response',
        'created_at',
    ),
    'support_policy': (
        'policy_id',
        'title',
        'category',
        'policy_text',
        'effective_date',
        'source_type',
    ),
    'resolution_playbook': (
        'playbook_id',
        'title',
        'category',
        'trigger_conditions',
        'recommended_steps',
        'escalation_rules',
        'source_type',
    ),
    'evaluation_question': (
        'question_id',
        'question',
        'expected_case_ids',
        'expected_policy_ids',
        'expected_playbook_ids',
        'answer_type',
        'notes',
    ),
}

OPTIONAL_SUPPORT_CASE_FIELDS = (
    'source_dataset',
    'source_license',
    'source_record_id',
)


def _require_fields(record: dict[str, Any], schema_name: str) -> None:
    missing = [field for field in REQUIRED_FIELDS[schema_name] if field not in record]
    if missing:
        raise ValueError(f"Missing required fields for {schema_name}: {missing}")


def _reject_unknown_fields(record: dict[str, Any], allowed_fields: set[str], schema_name: str) -> None:
    unexpected = sorted(set(record) - allowed_fields)
    if unexpected:
        raise ValueError(f"Unexpected fields for {schema_name}: {unexpected}")


def _require_non_empty_text(record: dict[str, Any], fields: tuple[str, ...], schema_name: str) -> None:
    for field in fields:
        value = record[field]
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Field '{field}' must be a non-empty string for {schema_name}")


def _require_optional_text(value: Any, field_name: str, schema_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Field '{field_name}' must be a non-empty string when present for {schema_name}")
    return value


def _require_iso_date(value: str, field_name: str, schema_name: str) -> None:
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"Field '{field_name}' must be an ISO date for {schema_name}") from exc


def _require_string_list(value: Any, field_name: str, schema_name: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        raise ValueError(f"Field '{field_name}' must be a list of non-empty strings for {schema_name}")
    return value


def validate_support_cases(records: list[dict[str, Any]]) -> list[SupportCase]:
    validated: list[SupportCase] = []
    seen_ids: set[str] = set()
    allowed_fields = set(REQUIRED_FIELDS['support_case']) | set(OPTIONAL_SUPPORT_CASE_FIELDS)
    for record in records:
        _require_fields(record, 'support_case')
        _reject_unknown_fields(record, allowed_fields, 'support_case')
        _require_non_empty_text(record, REQUIRED_FIELDS['support_case'], 'support_case')
        _require_iso_date(record['created_at'], 'created_at', 'support_case')
        case_id = record['case_id']
        if case_id in seen_ids:
            raise ValueError(f'Duplicate support case id: {case_id}')
        seen_ids.add(case_id)
        validated.append(
            SupportCase(
                case_id=record['case_id'],
                customer_message=record['customer_message'],
                category=record['category'],
                intent=record['intent'],
                product_area=record['product_area'],
                priority=record['priority'],
                status=record['status'],
                resolution_summary=record['resolution_summary'],
                agent_response=record['agent_response'],
                created_at=record['created_at'],
                source_dataset=_require_optional_text(record.get('source_dataset'), 'source_dataset', 'support_case'),
                source_license=_require_optional_text(record.get('source_license'), 'source_license', 'support_case'),
                source_record_id=_require_optional_text(record.get('source_record_id'), 'source_record_id', 'support_case'),
            )
        )
    return validated


def validate_support_policies(records: list[dict[str, Any]]) -> list[SupportPolicy]:
    validated: list[SupportPolicy] = []
    seen_ids: set[str] = set()
    for record in records:
        _require_fields(record, 'support_policy')
        _require_non_empty_text(record, REQUIRED_FIELDS['support_policy'], 'support_policy')
        policy_id = record['policy_id']
        if policy_id in seen_ids:
            raise ValueError(f'Duplicate support policy id: {policy_id}')
        seen_ids.add(policy_id)
        validated.append(SupportPolicy(**record))
    return validated


def validate_resolution_playbooks(records: list[dict[str, Any]]) -> list[ResolutionPlaybook]:
    validated: list[ResolutionPlaybook] = []
    seen_ids: set[str] = set()
    for record in records:
        _require_fields(record, 'resolution_playbook')
        _require_non_empty_text(record, REQUIRED_FIELDS['resolution_playbook'], 'resolution_playbook')
        playbook_id = record['playbook_id']
        if playbook_id in seen_ids:
            raise ValueError(f'Duplicate resolution playbook id: {playbook_id}')
        seen_ids.add(playbook_id)
        validated.append(ResolutionPlaybook(**record))
    return validated


def validate_evaluation_questions(records: list[dict[str, Any]]) -> list[EvaluationQuestion]:
    validated: list[EvaluationQuestion] = []
    seen_ids: set[str] = set()
    for record in records:
        _require_fields(record, 'evaluation_question')
        _require_non_empty_text(
            record,
            ('question_id', 'question', 'answer_type', 'notes'),
            'evaluation_question',
        )
        question_id = record['question_id']
        if question_id in seen_ids:
            raise ValueError(f'Duplicate evaluation question id: {question_id}')
        seen_ids.add(question_id)
        validated.append(
            EvaluationQuestion(
                question_id=record['question_id'],
                question=record['question'],
                expected_case_ids=_require_string_list(record['expected_case_ids'], 'expected_case_ids', 'evaluation_question'),
                expected_policy_ids=_require_string_list(record['expected_policy_ids'], 'expected_policy_ids', 'evaluation_question'),
                expected_playbook_ids=_require_string_list(record['expected_playbook_ids'], 'expected_playbook_ids', 'evaluation_question'),
                answer_type=record['answer_type'],
                difficulty=_require_optional_text(record.get('difficulty'), 'difficulty', 'evaluation_question'),
                notes=record['notes'],
            )
        )
    return validated


def serialize_dataclasses(records: list[Any]) -> list[dict[str, Any]]:
    """Convert validated dataclass instances into dictionaries."""
    return [asdict(record) for record in records]
