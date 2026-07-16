# Tool Review Checklist

## Source and supply chain

- Confirm the canonical publisher and repository.
- Confirm the package name is not a typo-squatted variant.
- Prefer a pinned release, digest, or commit for sensitive use.
- Check license, security policy, release history, and known advisories.
- Identify install scripts, native binaries, containers, transitive dependencies, and auto-update behavior.
- Distinguish signed or namespace-verified publication from an actual security audit.

## Permissions and execution

- List file paths, environment variables, network endpoints, accounts, devices, browser state, databases, and system resources accessed.
- Separate read, write, delete, execute, and administrative privileges.
- Check whether the tool can run arbitrary commands or load untrusted extensions.
- Prefer project or user scope over system scope.

## Secrets and data

- Identify every credential type and requested scope.
- Never ask the user to paste secrets into chat when a secure native flow exists.
- Trace what data leaves the machine, the destination, retention, training use, and deletion controls when documented.
- Flag unknown telemetry or subprocess behavior.
- Use sample or synthetic data for initial verification when possible.

## Cost and operations

- State fixed price, usage price, free tier, quota, and possible runaway cost.
- Identify rate limits, availability dependencies, region constraints, and vendor lock-in.
- Check logs, health checks, timeout behavior, failure modes, and support status.

## Reversibility

- Document uninstall, configuration cleanup, token revocation, created resources, and data deletion.
- Back up configuration before an approved replacement.
- Prefer actions with dry-run, preview, transaction, undo, or rollback support.

## Decision rule

Recommend approval only when the capability benefit is material, required unknowns are resolved or accepted, permissions are proportionate, data handling is acceptable, and rollback is credible.
