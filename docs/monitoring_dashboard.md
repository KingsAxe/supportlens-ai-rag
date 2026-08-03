# Monitoring Dashboard

## Monitoring Scope

This phase adds submission-ready local monitoring and feedback tracking for the Streamlit reviewer workflow.

## Feedback Captured

The Ask SupportLens page now captures:

- answer generation events;
- 1 to 5 rating values;
- thumbs up or thumbs down feedback;
- optional free-text comments;
- retrieval metadata tied to the answer session.

## Event Schema

Monitoring events are written to:

- `data/processed/monitoring_events.jsonl`

Event types:

- `answer_generated`
- `feedback_submitted`

### `answer_generated`

Fields logged:

- `timestamp`
- `event_type`
- `question`
- `dataset_mode`
- `retrieval_method`
- `top_k`
- `prompt_version`
- `dry_run`
- `provider`
- `model`
- `latency_ms`
- `citation_count`
- `source_ids`
- `source_types`

### `feedback_submitted`

Fields logged:

- `timestamp`
- `event_type`
- `question`
- `rating`
- `thumbs`
- `feedback_text`
- `dataset_mode`
- `retrieval_method`
- `top_k`
- `prompt_version`
- `dry_run`
- `citation_count`
- `source_ids`

No secrets are logged.

## Dashboard Charts

The monitoring dashboard now includes at least these useful visuals:

1. questions generated over time;
2. feedback submissions over time;
3. rating distribution;
4. thumbs up vs thumbs down;
5. dataset mode usage;
6. prompt version usage;
7. source type distribution;
8. latency distribution;
9. dry-run vs real-mode usage.

The page also shows summary metric cards for:

- total answers generated;
- total feedback submissions;
- average rating;
- thumbs up count;
- thumbs down count;
- average latency.

## Demo Monitoring Events

For reviewer convenience, the monitoring dashboard provides a button:

- `Create demo monitoring events`

This writes a small synthetic monitoring log into the ignored local monitoring file so the dashboard can be reviewed without manually creating many interactions.

## Why Logs Are Stored Under `data/processed/`

Monitoring logs are local runtime artifacts, similar to generated chunks, metrics, and RAG run logs. They belong under `data/processed/` because they are derived from application use rather than committed benchmark data.

## Why Monitoring Logs Are Not Committed

Monitoring logs are intentionally excluded from git because:

- they are reviewer- or developer-generated runtime data;
- they may vary between sessions;
- they should not pollute the reproducible committed sample dataset;
- they are not source files.

## Limitations

- Monitoring is local and file-backed only in this phase.
- There is no multi-user persistence or authentication.
- The dashboard is intended for submission review, not production observability.
- Real LLM usage remains optional and untested here because live provider quota access is still blocked.
