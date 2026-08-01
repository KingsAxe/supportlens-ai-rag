# SupportLens AI Data Strategy

## Goals

The data plan is designed to be public, reproducible, reviewable, and safe to share in a public repository.

## Planned Data Sources

### Public customer-support utterances or tickets

The project will use one or more public support-style datasets or conversation datasets that can stand in for historical customer support cases. Selection criteria:

- public availability;
- reproducible download or packaging path;
- enough structure to derive issue types, resolutions, or conversation context;
- compatibility with local development constraints.

### Generated support policy documents

The project will include generated or manually authored support policy documents such as:

- refund policy examples;
- account access policy examples;
- escalation policy examples;
- shipping or billing policy examples.

These documents are intended to simulate internal knowledge artifacts without using private business data.

### Generated resolution playbooks

The project will include generated or manually authored resolution playbooks such as:

- password reset handling;
- duplicate charge resolution;
- delayed shipment response flow;
- account verification escalation flow.

### Sample dataset for reviewers

`data/sample/` will hold a small, reviewer-friendly subset that supports reproducible demos and evaluation examples without requiring a large external download during initial review.

## Data Governance Constraints

- No private support data.
- No customer PII intentionally included.
- No repository secrets.
- No DataTalksClub FAQ data.

## Planned Data Layers

- `data/raw/` for non-committed or externally sourced raw artifacts.
- `data/processed/` for generated intermediate outputs, typically ignored from git.
- `data/sample/` for small committed examples safe for reviewers.

## Planned Metadata

Each document or chunk is expected to carry metadata such as:

- source type;
- source identifier;
- support category;
- timestamp if available;
- chunk identifier;
- synthetic or public provenance marker.