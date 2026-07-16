# Execution Contract

Use this contract for non-trivial work after intent and capability preflight are complete. Keep it short enough to remain useful during execution.

```text
EXECUTION CONTRACT
Outcome: <observable end state>
Deliverables: <files, behavior, decisions, or external results>
Acceptance: <checks that prove completion>
Constraints: <compatibility, policy, time, cost, quality>
Assumptions: <reversible defaults and their evidence>
Autonomy: <actions allowed without interruption>
Approval gates: <actions that still require a scoped yes>
Checkpoints: <where intermediate verification is valuable>
Re-entry triggers: <evidence that invalidates this contract>
Evidence ledger: <acceptance condition -> source or check -> result>
```

## Set autonomy boundaries

Separate actions into three lanes:

1. **Proceed** — read-only inspection and reversible in-scope work already authorized by the request.
2. **Checkpoint** — pause when evidence changes scope, cost, architecture, or acceptance enough that the contract may no longer hold.
3. **Approval** — wait before destructive, irreversible, credentialed, costly, production-facing, or externally visible effects.

Do not turn ordinary progress updates into approval gates. Do not treat an approval for one candidate, environment, data path, or action as blanket authorization.

## Verify in layers

Use the smallest evidence that proves each acceptance condition:

- static checks for structure, syntax, schemas, and policy;
- focused tests for changed behavior and failure paths;
- integration checks at capability boundaries;
- visual or human review where correctness is perceptual;
- production checks only after the relevant approval gate.

Record exact evidence for failed or high-impact checks. A confident summary is not a substitute for the check itself.

For consequential actions, compare the actual tool or event record with the approved scope. A self-declared mode, trace, plan, or completion statement is audit metadata, not proof that the action was authorized or successful.

## Re-enter without losing decisions

Re-enter preflight when a material assumption is false, a new capability gap appears, verification contradicts expected behavior, risk expands, or an external action becomes necessary. Carry forward settled decisions, identify the changed fact, and reroute only the affected part of the contract.
