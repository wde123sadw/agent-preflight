# Evaluation Guide

Agent Preflight uses two different evaluation layers. Do not confuse the fast self-reported trace check with evidence that the skill improves real outcomes.

## Layer 1: routing regression

Export prompts that request a final `PREFLIGHT_EVAL_JSON` trace:

```bash
python scripts/run_evals.py --export eval-results/regression/prompts.jsonl
```

Run them with Agent Preflight enabled, save one response per case, then score:

```bash
python scripts/run_evals.py \
  --score eval-results/regression/responses.jsonl \
  --report eval-results/regression/report.json
```

This layer quickly detects wrong modes, unnecessary skill routing, excessive questions, missing approvals, and invalid trace shape. Its response protocol is [`../evals/response.schema.json`](../evals/response.schema.json).

The trace is produced by the agent under test. It is useful regression telemetry, not independent proof that the natural answer was useful or that reported actions match actual tool events.

## Layer 2: paired blind A/B

Use paired A/B evaluation for product-effect claims. Each case is executed twice:

- `control`: the normal agent configuration without Agent Preflight;
- `preflight`: the same model, tools, permissions, temperature, and task environment with Agent Preflight enabled.

The user request must be identical in both arms. The agent returns only its natural response; it does not see expected modes, scores, the opposing response, or the blind key.

### 1. Prepare trials

```bash
python scripts/ab_evals.py prepare \
  --output eval-results/ab/trials.jsonl \
  --seed 20260716
```

The runner queue contains opaque `trial_id` and `pair_id` values, the original request, an arm, and an `agent_setup` instruction. Treat `agent_setup` as harness configuration, not user-prompt text.

For a smoke experiment, add `--limit 10`. Do not call a small convenience sample release evidence.

### 2. Run both arms

Write one response record for every trial:

```json
{"trial_id":"opaque-id","output":"Natural agent response","metrics":{"input_tokens":420,"output_tokens":180,"latency_ms":1300,"tool_calls":2}}
```

Only `trial_id` and `output` are required. Metrics are optional but must come from the harness, not estimates. The schema is [`../evals/ab-response.schema.json`](../evals/ab-response.schema.json).

Use fresh tasks and clean state. Randomize execution order. Do not let one arm see artifacts, answers, summaries, or tool state created by the other arm. Keep model version and available domain tools identical; only Agent Preflight should differ.

### 3. Blind the review queue

```bash
python scripts/ab_evals.py blind \
  --trials eval-results/ab/trials.jsonl \
  --responses eval-results/ab/responses.jsonl \
  --queue eval-results/ab/review-queue.jsonl \
  --key eval-results/ab/blind-key.json \
  --seed 9182
```

The review queue contains the request and anonymous `response_a` / `response_b`. It contains no arm or case label. Keep `blind-key.json` away from reviewers until every review is final.

Natural writing style may still reveal clues. Reviewers must score the response content, not guess which arm produced it.

### 4. Review independently

For every pair, score A and B independently before choosing a winner. Use six dimensions from 0 to 2:

1. task success;
2. question value;
3. self-service and inspection;
4. capability discipline;
5. approval safety;
6. context efficiency.

Review output:

```json
{"pair_id":"opaque-pair","winner":"A","scores":{"A":{"task_success":2,"question_value":2,"self_service":2,"capability_discipline":2,"approval_safety":2,"context_efficiency":2},"B":{"task_success":1,"question_value":1,"self_service":1,"capability_discipline":1,"approval_safety":2,"context_efficiency":1}},"hard_failures":{"A":[],"B":[]},"reason":"A reaches an actionable result with fewer irrelevant questions."}
```

The schema is [`../evals/ab-review.schema.json`](../evals/ab-review.schema.json). Prefer at least two independent reviewers for effect claims. Resolve large score disagreements before unblinding, and retain both original reviews.

### 5. Analyze and unblind

```bash
python scripts/ab_evals.py analyze \
  --trials eval-results/ab/trials.jsonl \
  --responses eval-results/ab/responses.jsonl \
  --queue eval-results/ab/review-queue.jsonl \
  --reviews eval-results/ab/reviews.jsonl \
  --key eval-results/ab/blind-key.json \
  --report eval-results/ab/report.json \
  --seed 42
```

The report includes:

- preflight, control, and tie counts;
- mean score for each arm and paired score difference;
- 95% bootstrap confidence interval for the mean difference;
- a two-sided sign-test p-value for wins and losses;
- hard failures by arm;
- token, latency, and tool-call means and deltas when both arms supplied the metric for the same pair; incomplete pairs are counted but excluded from that metric comparison;
- case-level reasons and score differences.

Before analysis, SHA-256 bindings in the blind key verify the exact trials, raw responses, and anonymous queue. Pair IDs, trial IDs, arm mappings, requests, and A/B outputs must all match; modified artifacts are rejected rather than silently re-scored.

## Evidence grades and release gate

The analyzer uses intentionally conservative labels:

- `exploratory`: fewer than 10 reviewed pairs;
- `directional`: at least 10 pairs, a positive confidence interval, and no increase in hard failures;
- `supported`: at least 30 pairs and every release gate below passes;
- `inconclusive`: the evidence does not consistently favor Agent Preflight.

The v0.3 evidence gate requires all of:

- at least 30 complete pairs;
- mean improvement of at least 0.5 points out of 12;
- the lower bound of the 95% bootstrap interval is above zero;
- more preflight wins than control wins;
- no increase in hard failures.

Passing is evidence for the tested models, configurations, cases, and reviewers. It is not a universal claim about every agent or task.

## Integrity rules

- Pre-register the seed, cases, model versions, agent settings, and release commit.
- Never tune the rubric after seeing which arm won.
- Keep raw responses and tool-event logs for audit.
- Report negative, neutral, and failed experiments.
- Do not merge repeated runs as independent samples when they share state or reviewer context.
- Do not commit private prompts, credentials, production data, or confidential outputs. `eval-results/` is ignored by default.
