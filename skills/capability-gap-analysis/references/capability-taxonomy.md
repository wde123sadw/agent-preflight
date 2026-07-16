# Capability Taxonomy

Use this taxonomy to avoid jumping from a task directly to a brand name.

| Class | Examples of capabilities |
|---|---|
| Understand | parse a format, interpret a schema, inspect UI state, read project conventions |
| Retrieve | search files, fetch official docs, query a database, access a repository or SaaS record |
| Transform | edit code, convert media, clean data, modify documents, migrate schemas |
| Generate | create text, images, audio, video, diagrams, code, tests, structured artifacts |
| Execute | run commands, control a browser or app, call an API, deploy, publish, schedule |
| Verify | compile, test, render, diff, lint, preview, measure, audit, reproduce |
| Persist | save files, update external records, commit, upload, write database state |
| Coordinate | ask users, message collaborators, create tasks, wait for external state |
| Context | filter, index, summarize, compress, retrieve exact source, manage provenance |
| Govern | authenticate, authorize, log, approve, rollback, enforce policy, handle secrets |

## Capability statement format

Write requirements as:

```text
<verb> <object> [to quality/format] [under constraints] [with verification]
```

Example:

```text
Render a DOCX to page images on Windows while preserving fonts, then visually verify every page.
```

This is more useful than “need a Word tool.” It reveals that creation, rendering, font availability, and visual verification are separate capabilities.

## False gaps

Before declaring a gap, check for:

- a project dependency that already exposes the function;
- an installed CLI hidden behind a task runner;
- a built-in connector with the required authenticated state;
- a simpler transformation that avoids the specialized tool;
- a read-only API sufficient for the requested report;
- a manual user step that is cheaper and safer than permanent installation.
