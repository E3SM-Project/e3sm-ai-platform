# E3SM AI Platform documentation

This directory is the documentation entry point for the current E3SM AI Platform
prototype, focused on E3SM Compass.

## User

- [Usage guide](user/usage.md): run the prototype locally and submit assistant
  questions.

## Development

- [Setup](dev/setup.md): install dependencies, configure local services, and
  run validation commands.
- [Architecture](dev/architecture.md): current backend, frontend, retrieval,
  routing, generation, and extension boundaries.
- [Observability](dev/observability.md): observability guidance and local
  tracing workflow.

## Corpus

- [Curation](corpus/curation.md): source scope, reproducible local corpus
  builds, question coverage, and opt-in runtime use.
- [Review checklist](corpus/review.md): steps to approve and package a corpus
  build.

## Evaluation

- [Synthetic questions](evaluation/1-synthetic-questions.md): how the
  100-question evaluation set was generated, its coverage, and what needs
  review.
- [Scoring](evaluation/2-scoring.md): in-progress retrieval and answer quality
  metrics and baseline results.
- [Contract](evaluation/3-contract.md): deterministic integration evaluation and
  the adapter contract.

## Repository areas

- `backend/`: FastAPI E3SM Compass service and packaged evaluator adapter.
- `frontend/`: React, TypeScript, and Vite chat UI.
- `evaluation/`: independent deterministic pytest suite for response-contract
  checks.
