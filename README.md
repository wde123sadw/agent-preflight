# Agent Preflight

**Clarify the task. Find the capability. Approve before action.**

[![CI](https://github.com/wde123sadw/agent-preflight/actions/workflows/ci.yml/badge.svg)](https://github.com/wde123sadw/agent-preflight/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/wde123sadw/agent-preflight)](https://github.com/wde123sadw/agent-preflight/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Agent Preflight is an adaptive skill pack for AI agents. It helps an agent decide when to ask questions, when to inspect first, when a task has a real capability gap, where to discover tools, what the user must review, and how to control context cost without losing evidence.

It is designed to improve outcomes without turning every request into an interview.

## Why

Agent failures often begin before execution:

- the request had multiple valid interpretations;
- the agent asked for information it could have inspected;
- a missing capability was discovered too late;
- a tool was installed because it looked popular, not because it was fit and safe;
- large logs or search results consumed the context window;
- assumptions were never converted into acceptance criteria.

Agent Preflight addresses those failures as a small, composable workflow.

## What's new in v0.2.0

- **Uncertainty routing:** classify unknowns as discover, assume, ask, or gate before interrupting the user.
- **Execution contracts:** make autonomy, acceptance evidence, checkpoints, and re-entry triggers explicit.
- **Scorable forward evals:** export prompts, ingest machine-readable traces, and enforce release thresholds.
- **Transactional installation:** preflight collisions, back up forced replacements, roll back failures, and verify every copied file.
- **Installation doctor:** detect missing, changed, and unexpected files in an installed pack.
- **Cross-platform CI:** validate the pack and run unit tests on Windows and Linux with Python 3.8 and 3.12.

## How it behaves

| Request | Expected behavior |
|---|---|
| `1 + 1 = ?` | Answer directly |
| “Change this button to red” | Inspect the project, then make the clear low-risk change |
| “Add subscriptions” | Clarify users, business behavior, failure paths, and acceptance criteria |
| “Use a tool to edit this video” | Check installed capabilities, identify a gap, then discover candidates |
| “Install this MCP and connect production data” | Review source, permissions, data path, secrets, cost, and rollback; wait for approval |
| “Analyze this 100k-line log” | Filter and index first; compress only when useful and recoverable |

## Skills

- `using-agent-preflight` — route the task through the smallest useful preflight.
- `intent-preflight` — clarify material ambiguity using relevant professional lenses.
- `capability-gap-analysis` — inventory existing capabilities before seeking more.
- `tool-discovery` — search trustworthy sources for a precisely defined gap.
- `tool-review-gate` — present safety, cost, permission, and rollback information for approval.
- `context-budget` — reduce context cost while preserving exact evidence and provenance.

## Core safety rule

Read-only inspection and candidate discovery may proceed when in scope. Installing, enabling, authenticating, changing shared configuration, sending data to a new third party, spending money, publishing, deploying, deleting, or migrating requires explicit user approval.

## Install

Preview the complete install plan without writing:

```bash
python scripts/install.py --dry-run
```

Install to the default Codex skill directory:

```bash
python scripts/install.py
```

Codex on Windows:

```powershell
./scripts/install.ps1
```

Custom target:

```powershell
./scripts/install.ps1 -Target "$HOME/.codex/skills"
```

Unix-like systems:

```bash
./scripts/install.sh "${CODEX_HOME:-$HOME/.codex}/skills"
```

The installer copies individual folders from `skills/`. It refuses to overwrite an existing skill unless the explicit force option is used; forced replacements are backed up first.

After installation, verify exact file integrity:

```bash
python scripts/doctor.py
```

Use `--target <skill-root>` with either command for another compatible agent. Run `python scripts/install.py --help` for dry-run, force, target, and JSON output options.

## Validate

```bash
python scripts/validate_pack.py
python scripts/run_evals.py --check
python -m unittest discover -s tests -v
```

The first command validates skill structure, metadata, references, scripts, protocol synchronization, and approval language. The second validates the behavior corpus and prints coverage.

To run a real forward evaluation, export prompts, execute them with the agent under test, and score its JSONL responses:

```bash
python scripts/run_evals.py --export eval-results/prompts.jsonl
python scripts/run_evals.py --score eval-results/responses.jsonl --report eval-results/report.json
```

The response protocol is defined in [`evals/response.schema.json`](evals/response.schema.json), with integration examples in [`docs/evaluation.md`](docs/evaluation.md). A release candidate must have no hard failures, average at least 10/12, and select the exact mode in at least 90% of cases. Automated trace scoring is a routing and safety gate; use [`evals/rubric.md`](evals/rubric.md) for qualitative forward review.

## Design principles

1. **Adaptive, not ceremonial.** Simple work should remain simple.
2. **Inspect before asking.** Do not outsource discoverable facts to the user.
3. **Capability before product.** Define the missing capability before searching brand names.
4. **Local before external.** Reuse installed and project-native tools first.
5. **Discovery is not approval.** Never turn a search result into an installation decision.
6. **Reduce before compressing.** Filter, paginate, and select before lossy transformation.
7. **Evidence over confidence.** Verify behavior, sources, and task acceptance conditions.

## Project structure

```text
agent-preflight/
├── agent-preflight.json  # Versioned pack manifest
├── skills/               # Installable skills
├── evals/                # Behavior cases, trace schema, and rubric
├── scripts/              # Installer, doctor, validation, and eval utilities
├── tests/                # Cross-platform unit tests
└── docs/                 # Architecture and policy documentation
```

## Inspiration

The lifecycle routing and verification discipline are inspired by [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills). Capability matrices and scoped preflight ideas are inspired by [HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything). Agent Preflight is an independent project and does not copy or bundle either project.

## Status

`v0.2.0` — evaluation and reliability release. See [CHANGELOG.md](CHANGELOG.md) for details.

## License

MIT
