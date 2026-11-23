# E3SM Compass evaluation contract

This independent pytest suite checks the response contract without live LLM or
web requests. For the broader quality baseline, see the
[scoring guide](docs/2-scoring.md) and [synthetic questions](docs/1-synthetic-questions.md).

## Run the suite

From the repository root, run `make evaluation-test`, or run the equivalent
command with the packaged backend adapter:

```sh
E3SM_COMPASS_EVALUATOR=e3sm_ai_platform.evaluation:evaluate \
  uv run --all-packages pytest evaluation
```

`--all-packages` makes both workspace packages available. Without
`E3SM_COMPASS_EVALUATOR`, the tests skip. For lint and type checks, run
`make evaluation-lint` and `make evaluation-typecheck`.

## Adapter contract

Pytest imports the adapter once per session and calls it for each fixture
question. The adapter must be synchronous: `evaluate(question: str) ->
Mapping[str, object]`. Return a mapping with these fields:

```python
{
    "answer": "...",
    "route": "curated",
    "retrieved_evidence": [{"source_id": "user-guide:compsets", "text": "..."}],
    "citations": [{"source_id": "user-guide:compsets", "provenance": "..."}],
    "insufficient_evidence": False,
}
```

- `route` must be `curated`, `web`, `future_operational`, or `insufficient_evidence`.
- `retrieved_evidence` must be a flat list of records with `source_id`. Each
  citation must include `source_id` and `provenance`.
- For curated cases, retrieved evidence must include the source IDs expected by
  [the fixtures](fixtures/e3sm_questions.json). Translate backend IDs if needed.
- For unsupported cases, use the `insufficient_evidence` route, set the boolean
  `insufficient_evidence` to `True`, return no retrieved evidence, and state in
  the answer that evidence is insufficient.

The packaged adapter uses the backend query service. An HTTP adapter can call
`POST /query` and normalize the response; keep HTTP details out of the tests.
