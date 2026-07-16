# Routing Policy

## Decision order

Evaluate in this order because later checks can only add caution:

1. Is the request answerable and low-risk as written?
2. Can read-only inspection resolve missing facts?
3. Do unresolved decisions materially change the result?
4. Are required capabilities actually available?
5. Would any action cross an approval boundary?
6. Will context size or repetition impair reasoning?

## Signals

| Signal | Route |
|---|---|
| Pure factual or arithmetic question | `DIRECT` |
| Typo, explicit rename, or mechanical format change | `DIRECT` or `INSPECT` |
| Existing project behavior is unknown | `INSPECT` |
| Missing user, outcome, success measure, or binding constraint | `CLARIFY` |
| Multiple reasonable product behaviors | `CLARIFY` |
| Long-running or multi-stage deliverable | `CLARIFY`, then execution contract |
| Required file, API, connector, renderer, browser, or runtime may be absent | `DISCOVER` |
| Install, credential, external data transfer, production mutation, money, deletion, or publication | `GATE` |
| Large logs, search results, repositories, datasets, or conversation history | add `$context-budget` |

## Common sequences

- Trivial answer: `DIRECT`
- Small code change: `INSPECT` -> execute -> verify
- New feature: `$intent-preflight` -> execution contract -> execute -> verify
- Missing tool: `$capability-gap-analysis` -> `$tool-discovery` -> `$tool-review-gate` -> user approval -> execute
- Production migration: `$intent-preflight` -> `$capability-gap-analysis` -> `$tool-review-gate` -> explicit approval -> staged execution -> verification
- Large research task: `$intent-preflight` -> `$context-budget` -> source discovery -> synthesis -> evidence check

## Anti-patterns

- Do not invoke every skill because the pack exists.
- Do not ask users for facts available in the workspace.
- Do not search marketplaces before proving a capability gap.
- Do not recommend installation solely because a tool is popular.
- Do not treat a registry listing as a security review.
- Do not compress exact evidence and then verify against only the summary.
- Do not keep interviewing after the task is actionable.
