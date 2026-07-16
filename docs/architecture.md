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

The evaluation protocol separates the agent's natural response from a final structured trace. Deterministic scoring checks routing and approval behavior; qualitative review checks evidence, reasoning quality, and task-specific usefulness.

## Portability

The core workflows use standard `SKILL.md` files. Platform-specific adapters may be added around the pack, but the core must not assume one marketplace, browser, shell, or MCP implementation.

## Non-goals

- operating a new tool marketplace;
- automatically installing discovered tools;
- assigning a universal security score;
- replacing domain-specific implementation skills;
- compressing all model traffic without an explicitly configured provider;
- forcing a formal specification for every request.
