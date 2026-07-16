---
name: using-agent-preflight
description: Route non-trivial, ambiguous, costly, long-running, or high-risk agent work through adaptive intent clarification, capability gap analysis, tool discovery and review, and context budgeting. Use at the start of build, change, diagnosis, research, creative, data, or automation tasks when wrong assumptions, missing capabilities, large context, irreversible actions, or meaningful time or money are plausible. Skip trivial self-contained questions and clear low-risk mechanical work.
---

# Using Agent Preflight

## Purpose

Run the smallest preflight that can materially reduce misunderstanding, capability failure, wasted context, or unsafe action. Do not turn preflight into ceremony.

## Select a mode

Choose one mode before acting:

| Mode | Use when | Behavior |
|---|---|---|
| `DIRECT` | The request is self-contained, low-risk, and immediately answerable | Answer or act without announcing preflight |
| `INSPECT` | Local files, configuration, docs, or installed tools can resolve uncertainty | Inspect read-only evidence first; ask only if ambiguity remains |
| `CLARIFY` | One to three decisions would materially change the result | Use `$intent-preflight` with a small question budget |
| `DISCOVER` | The outcome is understood but required capabilities may be missing | Use `$capability-gap-analysis`, then `$tool-discovery` only for proven gaps |
| `GATE` | Work is destructive, irreversible, credentialed, production-facing, costly, or externally visible | Clarify, review capabilities, and obtain explicit approval before the gated action |

Read [routing-policy.md](references/routing-policy.md) when mode selection or skill sequencing is uncertain.

Honor an explicit user profile (`fast`, `balanced`, `deep`, or `critical`) using [profiles.md](references/profiles.md). A profile changes interruption and evidence depth; it never removes an approval boundary.

## Run the workflow

1. Classify the request as answer, inspect, diagnose, change, create, research, automate, or operate.
2. Check whether the request is trivial and safe enough for `DIRECT`.
3. Inspect available evidence before asking the user for discoverable facts.
4. Invoke `$intent-preflight` when unresolved choices change scope, behavior, cost, risk, or acceptance.
5. Invoke `$capability-gap-analysis` before searching for any new tool.
6. Invoke `$tool-discovery` only for a named, proven capability gap.
7. Invoke `$tool-review-gate` before installing, enabling, authenticating, or sending data to a new capability.
8. Invoke `$context-budget` when inputs or tool outputs are likely to exceed roughly 2,000 tokens, contain heavy repetition, or accumulate across a long task.
9. Read [execution-contract.md](references/execution-contract.md) and produce a compact execution contract for non-trivial work.
10. Execute and verify against that contract.

## Respect approval boundaries

Perform read-only inspection and candidate discovery without approval when they are in scope. Obtain explicit approval before:

- installing or enabling a tool, skill, plugin, extension, package, or MCP server;
- changing global or shared configuration;
- authenticating an external service or requesting secrets;
- sending project data to a new third party;
- purchasing, subscribing, deploying, publishing, deleting, migrating, or making an irreversible change.

Treat approval as specific to the named candidate, version or source, scope, permissions, data path, and action. Do not convert approval to search into approval to install.

## Limit interruption

- Ask no question in `DIRECT` unless a hidden high-risk condition appears.
- Prefer silent inspection before questions in `INSPECT`.
- Ask one question at a time when its answer changes the next question.
- Batch two to five independent questions when the user can answer them efficiently.
- Attach a concrete guess or recommended default when it reduces answer effort.
- Accept “use your judgment” for reversible choices; surface the assumptions and continue.
- Never bypass approval for high-risk actions merely because the user delegated judgment.

## Emit a preflight brief

For `CLARIFY`, `DISCOVER`, or `GATE`, keep the handoff compact:

```text
PREFLIGHT
Mode: CLARIFY | DISCOVER | GATE
Profile: fast | balanced | deep | critical
Outcome: <what success means>
Known: <verified facts>
Unknowns: <decisions that still matter>
Capabilities: <available / missing>
Assumptions: <defaults the agent may use>
Approval gates: <actions requiring confirmation>
Re-entry triggers: <new evidence that would pause or reroute execution>
Next: <question, discovery, review, or execution>
```

Do not print this structure for trivial work.

## Exit preflight

Start execution when all are true:

- the outcome and acceptance conditions are actionable;
- material unknowns are answered or explicitly delegated;
- required capabilities are available;
- proposed new tools have been reviewed and approved when needed;
- high-risk actions have explicit approval;
- the context strategy preserves the evidence needed for verification.

Re-enter preflight only when new evidence changes scope, invalidates an assumption, exposes a capability gap, threatens acceptance, or introduces a new approval boundary. Do not restart the entire interview: preserve settled decisions and ask only about the new branch.
