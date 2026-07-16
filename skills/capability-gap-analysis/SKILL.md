---
name: capability-gap-analysis
description: Determine whether an agent already has the capabilities required for a task before recommending or installing anything new. Use when a task may require unfamiliar file formats, external services, browsers, desktop apps, media generation, databases, deployment access, specialized runtimes, large-context handling, or verification tools. Produce a capability map and hand only proven gaps to tool discovery.
---

# Capability Gap Analysis

## Goal

Translate the approved outcome into required capabilities, inventory what is already available, and identify the smallest real gap. Prefer reuse over acquisition.

## Define required capabilities

Describe capabilities without product names. Separate:

- required: the outcome cannot be completed or verified without it;
- preferred: improves quality, speed, or cost but has a viable fallback;
- optional: convenience only.

Read [capability-taxonomy.md](references/capability-taxonomy.md) when the task spans multiple systems or artifact types.

## Inventory locally first

Use in-scope read-only inspection to check:

1. built-in agent tools and active connectors;
2. installed skills, plugins, and MCP servers;
3. project scripts, dependencies, task runners, and documented commands;
4. operating-system CLIs and runtimes;
5. authenticated services already placed in scope;
6. existing data access, renderers, validators, and test tools;
7. native application automation or official APIs.

Do not expose secrets while inspecting configuration. Record capability presence and evidence, not secret values.

## Test fitness, not existence

A tool is available only when it can satisfy the actual requirement. Check:

- supported input and output formats;
- required version or platform;
- read versus write capability;
- authentication and permission scope;
- expected quality and reliability;
- verification or preview support;
- cost, quota, latency, and offline requirements;
- whether use would cross a user approval boundary.

Do not mark “browser available” as sufficient when the task requires an existing signed-in Chrome session and only an isolated browser exists.

## Choose reuse or gap

For each requirement, label it:

- `READY`: available and fit;
- `READY_WITH_LIMITS`: usable with named constraints;
- `FALLBACK`: achievable through a less ideal existing path;
- `GAP`: no fit capability is available;
- `GATED`: capability exists but requires approval, credentials, payment, or external effect.

Do not search externally for `READY` or optional capabilities.

## Emit a capability map

```text
CAPABILITY MAP
Outcome: <approved outcome>

Requirement | Priority | Status | Evidence | Constraint
<capability> | required | READY/GAP/... | <tool/file/check> | <limit>

Smallest proven gaps:
- <capability stated without a product name>

Fallbacks:
- <existing path and tradeoff>

Approval gates:
- <existing capability that still requires permission>
```

Hand each required `GAP` to `$tool-discovery`. Hand each `GATED` capability or any proposed acquisition to `$tool-review-gate`.

## Stop conditions

Stop when every required capability is `READY`, `READY_WITH_LIMITS`, `FALLBACK` accepted by the user, `GAP` ready for discovery, or `GATED` ready for review.

Do not install, enable, authenticate, or modify configuration in this skill.
