# Changelog

All notable changes to Agent Preflight are documented here.

## [0.3.0] - 2026-07-16

### Added

- Paired control-versus-preflight experiment preparation with identical user requests and opaque trial IDs.
- Anonymous A/B review queues plus separate blind keys to prevent arm-label leakage.
- Independent review schemas for task success, question value, self-service, capability discipline, approval safety, context efficiency, and hard failures.
- Automatic unblinding with paired score deltas, bootstrap confidence intervals, two-sided sign tests, win rates, hard-failure comparison, and optional complete-pair token, latency, and tool-call metrics.
- A conservative evidence gate requiring at least 30 complete pairs, a positive interval, a useful mean gain, more preflight wins, and no increase in hard failures.
- 21 adversarial cases covering prompt injection, contradictions, false gaps, delegation, scoped approval, and local re-entry.

### Changed

- Expanded the behavior corpus from 39 to 60 cases and improved language balance from 28/11 to 32/28 English/Chinese.
- Reframed self-reported trace scoring as a fast routing regression check rather than evidence of product effect.
- Reduced visible preflight ceremony and added evidence-ledger guidance for consequential execution.
- Added approval receipts that preserve the user's exact approved candidate, scope, environment, and constraints.
- Replaced unblinded qualitative review with a paired independent-review protocol.

## [0.2.0] - 2026-07-16

### Added

- A versioned pack manifest shared by validation, installation, health checks, and eval tooling.
- A machine-readable forward-evaluation response protocol and deterministic 12-point scorer.
- Transactional cross-platform installation with dry-run, JSON output, backup, rollback, and post-copy verification.
- An installation doctor that reports missing, changed, and unexpected files.
- Execution contracts with autonomy lanes, checkpoints, layered verification, and local re-entry triggers.
- Uncertainty classification and contradiction scanning before user questions.
- Cross-platform unit tests and GitHub Actions CI.
- Python 3.8+ support for the dependency-free project utilities.
- Structured GitHub behavior reports and pull-request evidence checklists.

### Changed

- Install wrappers now delegate to one tested Python implementation.
- Pack validation now checks manifest synchronization, response schema enums, Python syntax, orphaned references, and README version status.
- Forward-eval exports now require a strict machine-readable trace.

## [0.1.0] - 2026-07-16

- Initial public release with six composable preflight skills and 39 bilingual behavior cases.
