# Architecture

Agent Preflight separates orchestration from specialist policy so a trivial request does not load every workflow.

## Control plane

`using-agent-preflight` selects `DIRECT`, `INSPECT`, `CLARIFY`, `DISCOVER`, or `GATE`. It owns sequencing and cross-skill approval boundaries, but delegates detailed work.

## Specialist skills

- `intent-preflight` converts ambiguity into an intent contract.
- `capability-gap-analysis` converts the contract into a capability map.
- `tool-discovery` converts a proven gap into a sourced shortlist.
- `tool-review-gate` converts candidates into an approval decision.
- `context-budget` controls information volume across every phase.

## Data products

Each stage creates a compact artifact consumed by the next:

```text
request
  -> intent contract
  -> capability map
  -> candidate records
  -> approval card
  -> execution contract
  -> verification evidence
```

The artifacts are conversation structures, not mandatory files. Persist them only when the user requests a durable handoff or the task spans sessions.

## Reliability layer

`agent-preflight.json` is the single source of truth for release version, installed skills, modes, and profiles. The validator, installer, doctor, response schema, and evaluation runner must remain synchronized with it.

The installer uses a preflight-and-stage transaction:

```text
load manifest
  -> detect every collision
  -> stage all skills
  -> back up approved replacements
  -> install all skills
  -> compare exact file hashes
  -> keep backups on success or restore them on failure
```

The fast regression protocol separates the agent's natural response from a final structured trace. Deterministic scoring checks routing and approval behavior; the higher-trust A/B protocol independently reviews paired natural responses.

## Evaluation plane

Evaluation has two intentionally separate trust levels:

```text
self-reported trace
  -> fast routing regression
  -> detects obvious mode, question, skill, and gate drift

paired natural responses
  -> anonymous A/B queue
  -> independent scorecards and hard failures
  -> secret-key unblinding
  -> paired statistics and evidence grade
```

The control and preflight arms receive the same request. Arm configuration is runner metadata, not prompt text. Reviewers never receive expected modes, expected skills, case identifiers, or the blind key.

`ab_evals.py` calculates paired differences because each request acts as its own control. Bootstrap intervals describe uncertainty in the mean score difference; the sign test measures the direction of wins without assuming score normality. Neither statistic repairs a biased case set, leaked arm identity, shared run state, or non-independent reviewer.

Product-effect claims use verified natural outputs and independent reviews. Agent-generated traces remain telemetry and cannot prove authorization, external execution, or task success.

## Portability

The core workflows use standard `SKILL.md` files. Platform-specific adapters may be added around the pack, but the core must not assume one marketplace, browser, shell, or MCP implementation.

## Non-goals

- operating a new tool marketplace;
- automatically installing discovered tools;
- assigning a universal security score;
- replacing domain-specific implementation skills;
- compressing all model traffic without an explicitly configured provider;
- forcing a formal specification for every request;
- operating a hosted benchmark service or calling paid model APIs;
- claiming universal improvement from one model, reviewer, or case set.
