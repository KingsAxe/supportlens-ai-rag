"""Optional public dataset adapters for SupportLens AI."""

from __future__ import annotations

import argparse
import csv
import io
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import HTTPSHandler, ProxyHandler, Request, build_opener
import ssl

from src.ingestion.io import write_jsonl

BITEXT_SOURCE = 'bitext'
BITEXT_DATASET = 'bitext/Bitext-customer-support-llm-chatbot-training-dataset'
BITEXT_LICENSE = 'cdla-sharing-1.0'
BITEXT_CSV_URL = (
    'https://huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset/'
    'resolve/main/Bitext_Sample_Customer_Support_Training_Dataset_27K_responses-v11.csv'
)
DEFAULT_OUTPUT = Path('data/processed/public_support_cases_bitext.jsonl')

PRODUCT_AREA_BY_CATEGORY = {
    'ACCOUNT': 'account_management',
    'CANCEL': 'subscription_and_cancellation',
    'CONTACT': 'support_operations',
    'DELIVERY': 'order_fulfillment',
    'FEEDBACK': 'customer_experience',
    'INVOICE': 'billing_and_invoicing',
    'ORDER': 'order_management',
    'PAYMENT': 'payments',
    'REFUND': 'refunds_and_returns',
    'SHIPPING': 'shipping_and_addressing',
    'SUBSCRIPTION': 'communications',
}

HIGH_PRIORITY_INTENTS = {
    'complaint',
    'contact_human_agent',
    'payment_issue',
    'recover_password',
    'registration_problems',
}
LOW_PRIORITY_INTENTS = {
    'check_payment_methods',
    'delivery_options',
    'newsletter_subscription',
    'review',
}


def _clean_text(value: str) -> str:
    return ' '.join(value.split())


def _summarize_response(text: str, max_len: int = 220) -> str:
    clean = _clean_text(text)
    sentence_breaks = [clean.find(marker) for marker in ('. ', '! ', '? ') if clean.find(marker) != -1]
    if sentence_breaks:
        first_break = min(sentence_breaks) + 1
        if first_break <= max_len:
            return clean[:first_break].strip()
    if len(clean) <= max_len:
        return clean
    return clean[:max_len].rstrip() + '...'


def _derive_priority(category: str, intent: str) -> str:
    if intent in HIGH_PRIORITY_INTENTS:
        return 'high'
    if intent in LOW_PRIORITY_INTENTS:
        return 'low'
    if category in {'REFUND', 'INVOICE', 'ORDER', 'CANCEL', 'DELIVERY', 'SHIPPING'}:
        return 'medium'
    return 'medium'


def transform_bitext_row(row: dict[str, str], source_index: int, sample_index: int) -> dict[str, Any]:
    category = row['category'].strip()
    intent = row['intent'].strip()
    response = _clean_text(row['response'])
    created_at = (date(2025, 1, 1) + timedelta(days=source_index % 365)).isoformat()
    return {
        'case_id': f'bitext-case-{sample_index:04d}',
        'customer_message': _clean_text(row['instruction']),
        'category': category.lower(),
        'intent': intent,
        'product_area': PRODUCT_AREA_BY_CATEGORY.get(category, 'customer_support'),
        'priority': _derive_priority(category, intent),
        'status': 'resolved',
        'resolution_summary': _summarize_response(response),
        'agent_response': response,
        'created_at': created_at,
        'source_dataset': BITEXT_DATASET,
        'source_license': BITEXT_LICENSE,
        'source_record_id': f'bitext-row-{source_index:05d}',
    }


def _evenly_spaced_indices(count: int, target: int) -> list[int]:
    if target >= count:
        return list(range(count))
    if target == 1:
        return [0]
    indices = sorted({round(i * (count - 1) / (target - 1)) for i in range(target)})
    if len(indices) < target:
        extras = [index for index in range(count) if index not in indices]
        indices.extend(extras[: target - len(indices)])
        indices = sorted(indices[:target])
    return indices


def _select_balanced_rows(rows: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    if limit <= 0:
        raise ValueError('limit must be positive')
    if limit >= len(rows):
        return rows

    rows_by_intent: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        rows_by_intent[row['intent']].append(row)

    intents = sorted(rows_by_intent)
    base = limit // len(intents)
    remainder = limit % len(intents)
    selected: list[dict[str, Any]] = []

    for position, intent in enumerate(intents):
        target = base + (1 if position < remainder else 0)
        if target <= 0:
            continue
        intent_rows = rows_by_intent[intent]
        for index in _evenly_spaced_indices(len(intent_rows), target):
            selected.append(intent_rows[index])

    selected.sort(key=lambda row: row['_source_index'])
    return selected[:limit]


def _parse_bitext_csv(csv_text: str) -> list[dict[str, Any]]:
    reader = csv.DictReader(io.StringIO(csv_text))
    rows: list[dict[str, Any]] = []
    for source_index, row in enumerate(reader, start=1):
        rows.append(
            {
                'flags': row['flags'],
                'instruction': row['instruction'],
                'category': row['category'],
                'intent': row['intent'],
                'response': row['response'],
                '_source_index': source_index,
            }
        )
    return rows


def fetch_bitext_rows(timeout: float = 60.0) -> list[dict[str, Any]]:
    opener = build_opener(ProxyHandler({}), HTTPSHandler(context=ssl.create_default_context()))
    request = Request(BITEXT_CSV_URL, headers={'User-Agent': 'SupportLens AI public dataset adapter'})
    with opener.open(request, timeout=timeout) as response:
        csv_text = response.read().decode('utf-8')
    return _parse_bitext_csv(csv_text)


def build_bitext_support_case_records(limit: int) -> list[dict[str, Any]]:
    try:
        rows = fetch_bitext_rows()
    except (URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(
            'Failed to download the Bitext dataset. Use the committed sample file '
            'data/sample/public_support_cases_bitext.jsonl for reproducible local work.'
        ) from exc

    selected_rows = _select_balanced_rows(rows, limit)
    records: list[dict[str, Any]] = []
    for sample_index, row in enumerate(selected_rows, start=1):
        records.append(transform_bitext_row(row, row['_source_index'], sample_index))
    return records


def write_bitext_support_cases(limit: int, output_path: str | Path = DEFAULT_OUTPUT) -> Path:
    records = build_bitext_support_case_records(limit)
    output = Path(output_path)
    write_jsonl(output, records)
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Download and transform public support datasets')
    parser.add_argument('--source', default=BITEXT_SOURCE, choices=[BITEXT_SOURCE], help='Public dataset source to fetch')
    parser.add_argument('--limit', type=int, default=300, help='Number of records to transform into SupportLens schema')
    parser.add_argument(
        '--output',
        default=str(DEFAULT_OUTPUT),
        help='Output JSONL path relative to the current working directory',
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = write_bitext_support_cases(limit=args.limit, output_path=args.output)
    print('Public dataset transform completed')
    print(f'source={args.source}')
    print(f'limit={args.limit}')
    print(f'output={output_path.as_posix()}')


if __name__ == '__main__':
    main()
