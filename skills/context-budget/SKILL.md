---
name: context-budget
description: Control token and attention cost for tasks involving large files, logs, search results, repositories, datasets, tool outputs, long conversations, or repeated context. Use before reasoning over content likely to exceed roughly 2,000 tokens or when output quality degrades from context overload. Reduce at the source first, preserve provenance, use recoverable compression only when beneficial, and retrieve exact evidence before precise decisions.
---

# Context Budget

## Goal

Give the agent the smallest context that preserves the facts, relationships, and exact evidence required for the task. Optimize correctness before token count.

## Estimate the context shape

Identify:

- source type: code, logs, search results, JSON, table, prose, conversation, or binary-derived text;
- approximate size and repetition;
- exact details that must survive;
- whether the source can be queried again;
- whether summary, indexing, or compression is reversible;
- privacy and data-location constraints.

Skip context optimization for short inputs when the overhead would exceed the savings.

## Apply the reduction ladder

Use the first sufficient technique:

1. **Prevent** — request only needed fields, ranges, pages, files, or time windows.
2. **Filter** — search, rank, deduplicate, exclude boilerplate, and isolate errors or changed lines.
3. **Structure** — build an index, map, table, or hierarchical summary with source pointers.
4. **Summarize** — create a task-specific summary and retain provenance.
5. **Compress** — use a documented compressor when the content remains large and the transformation preserves required information.
6. **Retrieve** — recover exact source segments before quoting, patching, calculating, approving, or verifying.

Read [compression-policy.md](references/compression-policy.md) before using or recommending a compression system.

## Preserve evidence

For every transformed source, retain enough provenance to recover:

- source path, URL, query, tool call, or record identifier;
- line, page, row, timestamp, or section when available;
- transformation type and time;
- retrieval key or content hash when supported;
- details intentionally omitted.

Never cite a compressed summary as if it were the original source.

## Protect exactness

Retrieve or retain original content for:

- code patches, commands, API signatures, stack frames, and configuration;
- legal, policy, contractual, financial, and safety-critical language;
- credentials and secrets, which should not be sent to a compressor at all;
- structured data where every field or record matters;
- evidence used to approve a tool or high-risk action;
- user-requested quotations and precise citations.

## Discover compression tools only when justified

If repeated large-context work reveals a missing compression or retrieval capability:

1. describe the gap through `$capability-gap-analysis`;
2. discover current candidates through `$tool-discovery`;
3. review data flow, local/cloud behavior, accuracy evidence, and rollback through `$tool-review-gate`;
4. wait for approval before installation or proxy configuration.

Do not claim that an on-demand MCP tool automatically compresses prompts, hidden context, or all model traffic. Distinguish manual tool calls from proxy or middleware interception.

## Emit a context plan

For substantial tasks, state:

```text
CONTEXT PLAN
Need: <information required>
Sources: <where it lives>
Reduction: <filter/index/summary/compression>
Exact evidence retained: <what and where>
Retrieval trigger: <when original detail must be restored>
Expected benefit: <qualitative or measured>
Integrity risk: <what could be lost and mitigation>
```

After substantial compression, report measured savings when the tool provides them. Do not invent a savings percentage.
