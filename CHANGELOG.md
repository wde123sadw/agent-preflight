# Changelog

All notable changes to Agent Preflight are documented here.

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
