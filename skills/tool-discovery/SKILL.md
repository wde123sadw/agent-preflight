---
name: tool-discovery
description: Find a small shortlist of task-fit skills, plugins, MCP servers, CLIs, libraries, APIs, or applications for a proven capability gap. Use only after the required capability and current environment are understood. Search trustworthy and current sources, prefer official evidence, compare viable fallbacks, and return candidates for review without installing or enabling them.
---

# Tool Discovery

## Preconditions

Require all of the following:

- the task outcome is sufficiently clear;
- `$capability-gap-analysis` or equivalent inspection identified a named gap;
- the gap is required or the user asked for alternatives;
- read-only discovery is in scope.

If these are missing, return to clarification or capability analysis.

## Write the discovery query

Describe:

- required capability and artifact;
- platform and runtime;
- inputs, outputs, and quality bar;
- local, cloud, privacy, cost, and license constraints;
- required integration surface: Skill, plugin, MCP, CLI, library, API, or application;
- verification requirement.

Do not begin with a preferred brand unless the user required it.

## Search the right sources

Read [source-ladder.md](references/source-ladder.md). Search current sources because tools, versions, maintenance, and security change over time.

Prefer this order:

1. capabilities already exposed by the active agent platform;
2. official vendor tools, documentation, marketplaces, and package registries;
3. protocol or ecosystem registries with verifiable publisher identity;
4. established capability hubs such as CLI-Hub for agent-native professional software;
5. official GitHub repositories and releases;
6. community lists, discussions, and search results as leads only.

Use community popularity as a discovery signal, never as primary proof of fitness or safety.

## Verify each candidate

Use primary sources to record:

- canonical name, owner, URL, license, and current version or release;
- exact capability match and documented limits;
- supported platform, runtime, formats, and integration;
- installation and removal method;
- authentication, permissions, data flow, network use, and secret handling;
- pricing, quota, local/cloud execution, and vendor dependency;
- maintenance indicators and known security notices;
- documented verification, dry-run, health check, or preview path.

Clearly mark unknown fields. Do not fill them from memory.

## Limit the shortlist

Return at most three candidates by default:

- best fit;
- best low-risk or local alternative;
- best no-install fallback, when one exists.

Do not produce a marketplace dump. Explain why excluded tools are unnecessary only when the exclusion affects the decision.

## Emit candidate records

Use [candidate-record.md](references/candidate-record.md). Include source links beside supported claims. State whether discovery found no trustworthy fit.

End with a handoff to `$tool-review-gate`. Do not install, enable, authenticate, request credentials, or mutate configuration.
