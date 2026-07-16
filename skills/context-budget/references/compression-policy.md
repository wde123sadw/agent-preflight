# Compression Policy

## Decision table

| Content | Preferred treatment |
|---|---|
| Repetitive build logs | Filter errors and surrounding context; retain full log path |
| Search results | Rank, deduplicate, and keep top matches with source pointers |
| Large codebase | Build a project map; read exact files and symbols on demand |
| Long documentation | Extract relevant sections; retain deep links and headings |
| Tabular data | Project required columns and aggregate only when task permits |
| Strict JSON | Filter fields structurally; avoid free-form compression before tool reuse |
| Conversation history | Summarize decisions, open questions, evidence, and current state |
| Legal or financial text | Use index and excerpts; retain exact originals for decisions |

## Evaluate a compression provider

Review:

- local versus cloud processing;
- data retention, telemetry, and model-provider routing;
- supported content types and structural preservation;
- reversible retrieval and content-addressed storage;
- timeout and fail-open or fail-closed behavior;
- benchmark task similarity, not only headline savings;
- accuracy, entity preservation, code integrity, and citation fidelity;
- observability: original tokens, compressed tokens, transformations, and retrieval statistics;
- proxy scope and whether it affects all traffic or only explicit calls.

## Integrity test

Before relying on a new compressor, test representative material:

1. choose content similar to the real task;
2. define questions whose answers depend on exact entities, errors, and relationships;
3. answer from original and compressed versions independently;
4. compare correctness and missing evidence;
5. verify retrieval of omitted details;
6. accept only if savings are material and task accuracy is preserved.

## Failure rule

If compression loses a required fact, corrupts structure, prevents exact retrieval, or makes provenance ambiguous, fall back to filtering and selective reads. Token savings never justify unverifiable output.
