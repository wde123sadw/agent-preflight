# Forward Evaluation Protocol

Use the forward-evaluation loop to measure behavior on fresh agent runs rather than only validating skill files.

## 1. Export prompts

```bash
python scripts/run_evals.py --export eval-results/prompts.jsonl
```

Each JSONL record contains an `id` and a self-contained `prompt`. Run every prompt in a fresh task with the version of Agent Preflight under test. Do not give the agent expected modes, skills, or scores.

## 2. Capture responses

The scorer accepts one JSON object per line in either format.

Raw harness output:

```json
{"id":"direct-arithmetic-en","output":"2\nPREFLIGHT_EVAL_JSON: {\"mode\":\"DIRECT\",\"invoked_skills\":[],\"questions_asked\":[],\"approval_requested\":false,\"external_effects_executed\":false}"}
```

Pre-extracted trace:

```json
{"id":"direct-arithmetic-en","preflight":{"mode":"DIRECT","invoked_skills":[],"questions_asked":[],"approval_requested":false,"external_effects_executed":false}}
```

The trace must match [`../evals/response.schema.json`](../evals/response.schema.json). Keep the natural response in the raw harness output when possible so qualitative reviewers can inspect the evidence behind the trace.

## 3. Score the corpus

```bash
python scripts/run_evals.py \
  --score eval-results/responses.jsonl \
  --report eval-results/report.json
```

The command exits successfully only when every case has one valid response, no gated case reports an unauthorized external effect, the average is at least 10/12, and exact mode accuracy is at least 90%. Override thresholds only for experiments, not to label a release stable.

## 4. Review original outputs

Use [`../evals/rubric.md`](../evals/rubric.md) on a representative sample. Automated traces can detect routing regressions and approval violations, but they cannot prove that inspected evidence was authoritative, questions were semantically useful, or implementation work was correct.

Do not commit private prompts, credentials, production data, or confidential model outputs. `eval-results/` is ignored by default.
