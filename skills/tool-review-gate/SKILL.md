---
name: tool-review-gate
description: Review a proposed skill, plugin, MCP server, CLI, package, API, connector, application, or service before installation or use. Use when a new capability may execute code, access files or accounts, receive project data, require secrets, cost money, change configuration, or create external effects. Present a decision-ready approval card and wait for explicit, scoped user approval.
---

# Tool Review Gate

## Goal

Convert candidate information into a decision the user can safely approve, reject, or constrain. Discovery is not authorization.

## Establish the action under review

Name the exact:

- candidate and canonical source;
- version, commit, release, image, or package identifier when available;
- installation or enablement scope;
- requested permissions and credentials;
- data it will receive and where data travels;
- paid resources, quotas, or subscriptions;
- configuration and external effects;
- verification and rollback plan.

If the action is vague, do not request approval yet.

## Perform the review

Read [review-checklist.md](references/review-checklist.md). Verify claims using current primary sources and local read-only checks.

Rate each area independently as `LOW`, `MEDIUM`, `HIGH`, or `UNKNOWN`:

- source and supply chain;
- code execution and install scope;
- filesystem, network, account, and system permissions;
- secrets and authentication;
- data exposure, retention, and residency;
- financial and quota exposure;
- maintenance, compatibility, and vendor lock-in;
- reversibility and uninstall quality;
- operational blast radius.

Do not collapse `UNKNOWN` into low risk. Do not claim a complete security audit unless one was actually performed.

## Prefer the least-powerful option

Before recommending approval, consider:

- reuse of an existing tool;
- a project-scoped install instead of user or system scope;
- read-only mode before write access;
- dry-run, preview, sandbox, test account, or sample data;
- narrower API scopes;
- a local tool instead of external data transfer;
- a one-time manual step instead of a persistent integration;
- a pinned version and reproducible source.

If a lower-risk option still meets the requirement, recommend it.

## Present the approval card

Use [approval-card.md](references/approval-card.md). Keep facts, unknowns, inference, and recommendation distinguishable.

Offer explicit choices:

1. approve the exact proposed action;
2. approve with a narrower scope or condition;
3. use the no-install fallback;
4. request more evidence;
5. reject.

## Wait for scoped approval

Require an explicit choice before:

- installation, enablement, or update;
- authentication or credential entry;
- modification of global, shared, or production configuration;
- new external data transfer;
- payment, subscription, quota consumption, publication, deployment, deletion, or migration.

Approval must match the reviewed candidate and scope. A user saying “find a tool” is not approval. A user approving a local read-only test is not approval for account-wide write access.

## Execute safely after approval

When another workflow performs the approved action:

1. verify that the command and scope still match the approval card;
2. prefer dry-run or health check first;
3. capture version and installation evidence;
4. verify only the required capability;
5. avoid unrelated setup or optional telemetry;
6. report rollback or removal instructions;
7. stop if permissions, data flow, price, or source differs from the approved facts.

This skill reviews and gates. It does not silently execute the installation itself.
