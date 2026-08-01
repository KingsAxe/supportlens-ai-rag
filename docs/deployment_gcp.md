# SupportLens AI GCP Deployment Plan

## Planned Deployment Targets

Future deployment is planned around:

- Docker image;
- Artifact Registry;
- Cloud Run;
- Secret Manager;
- hosted PostgreSQL/pgvector option.

## Planned Environment Variables

Expected runtime configuration includes:

- `APP_ENV`
- `DATABASE_URL`
- `LLM_PROVIDER`
- `LLM_API_KEY`
- `LLM_BASE_URL`
- `LLM_MODEL`
- `EMBEDDING_MODEL`
- `GCP_PROJECT_ID`
- `GCP_REGION`

Real values must not be committed to the repository.

## Planned Deployment Flow

1. Build a Docker image.
2. Push the image to Artifact Registry.
3. Configure required runtime secrets in Secret Manager.
4. Deploy the service to Cloud Run.
5. Connect the application to a hosted database or vector-capable persistence layer if selected.
6. Run post-deployment checks.

## Hosted Database Option

One planned option is hosted PostgreSQL with `pgvector`, chosen for familiarity and support for both application state and vector search metadata. Final selection is deferred to a later phase.

## Deployment Validation Checklist

Planned validation items:

- container starts successfully;
- required environment variables are present;
- secrets are sourced from Secret Manager rather than the repository;
- database connectivity works;
- health endpoint or app startup completes cleanly;
- application can serve a basic test request;
- logs are visible for debugging;
- rollback path is documented.

## Current Status

This document is a future deployment blueprint only. No cloud deployment is performed in Phase 0.