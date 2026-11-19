# Scoring guide

In progress (#37). These definitions score retrieval and answer changes
against a baseline. `make corpus-coverage` reports only top-8 retrieval and
citation today; the other metrics and a retrieval-mode option are planned.

Metric implementations come from the evaluation framework chosen in #37
(task 2); definitions may be aligned to it. For the response contract test
suite, see [evaluation.md](evaluation.md).

Question sets, both in [`corpus/questions.json`](../../corpus/questions.json)
(method in [synthetic-questions.md](synthetic-questions.md)):

- **Answerable:** the 80 questions with `should_refuse` false.
- **Should refuse:** the 20 questions with `should_refuse` true.

## Metrics

Score each question, then average across questions unless noted.

| Metric | Definition | Set | LLM judge? |
| --- | --- | --- | --- |
| Recall@k | Share of expected documents in the top k | Answerable | No |
| MRR@k | 1 ÷ rank of the first expected document; 0 if none in the top k | Answerable | No |
| Cited recall | Share of expected documents cited | Answerable | No |
| Cited precision | Share of cited documents that are expected | Answerable | No |
| False refusal | Share of questions refused | Answerable | No |
| False answer | Share of questions answered | Should refuse | No |
| Latency | Median and p95 seconds per question | Both | No |
| Groundedness | Share of claims supported by cited evidence | Answerable | Yes |
| Answer quality | Match to a reference answer; measured once #38 provides them | Answerable | Yes |
| Cost | Total tokens × price | Both | No |

Terms:

- **k:** how many top-ranked chunks count as retrieved. Report k = 4 (the
  default `top_k`, the chunks the answer can cite) and k = 8 (the candidate
  set).
- **Expected document:** a document listed for a question in the question set.
- **Top k / rank:** a document is in the top k if any of its chunks is; its
  rank is its best chunk's rank.
- **Recall@k:** what share of expected documents retrieval finds. With 3
  expected documents and 2 in the top 8, Recall@8 is 0.67.
- **MRR@k (mean reciprocal rank):** how high the first expected document
  ranks. Rank 1 scores 1, rank 2 scores 0.5, rank 4 scores 0.25, and none in
  the top k scores 0.
- **Groundedness:** whether every claim in the answer is supported by the
  cited evidence. An answer can be grounded but still wrong if the evidence
  is wrong.
- **LLM judge:** a language model that grades answers. Results vary between
  runs and cost money.
- **p50 / p95:** the median, and the value 95% of questions finish within.

Also report the pooled count of expected documents in the top 8 (for example,
17/81) for comparison with #21.

## Guidelines

1. Use the same question sets and corpus snapshot for every run; rerun the
   baseline if either changes.
2. Change one setting per run, starting from the best run so far.
3. Keep a change only if recall or MRR clearly improves and refusal
   metrics do not get worse. A one- or two-question difference is noise.
   Confirm winners on the #38 expert questions before changing defaults.
4. Run LLM-judged metrics on finalist runs only.
5. Save per-question results and run metadata: corpus snapshot hash, commit,
   retrieval mode, k, reranker, and model.

## Results

One row per run. Each run changes one setting from its base run.

| Run | Based on | Change | Recall@4 | Recall@8 | MRR@8 | Cited recall | False refusal | False answer | Latency p50 | Keep? |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B1 | — | Lexical (default) | | | | | | | | Baseline |
| B2 | B1 | Semantic | | | | | | | | |
| B3 | B1 | Hybrid | | | | | | | | |
