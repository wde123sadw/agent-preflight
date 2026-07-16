#!/usr/bin/env python3
"""Transactionally install the Agent Preflight skill pack."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from packlib import ROOT, compare_skill, default_target, load_manifest


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def backup_path(destination: Path, timestamp: str) -> Path:
    candidate = destination.with_name(f"{destination.name}.bak.{timestamp}")
    sequence = 1
    while candidate.exists():
        candidate = destination.with_name(f"{destination.name}.bak.{timestamp}.{sequence}")
        sequence += 1
    return candidate


def install(target: Path, force: bool = False, dry_run: bool = False) -> dict:
    manifest = load_manifest()
    source_root = ROOT / "skills"
    target = target.expanduser().resolve()
    destinations = {name: target / name for name in manifest["skills"]}
    collisions = [name for name, path in destinations.items() if path.exists() or path.is_symlink()]

    if collisions and not force and not dry_run:
        raise FileExistsError(
            "existing skills would be replaced: " + ", ".join(collisions)
            + "; re-run with --force to back them up first"
        )

    report = {
        "pack": manifest["name"],
        "version": manifest["version"],
        "target": str(target),
        "dry_run": dry_run,
        "force": force,
        "skills": list(manifest["skills"]),
        "collisions": collisions,
        "ready": not collisions or force,
        "backups": {},
        "verified": False,
    }
    if dry_run:
        return report

    target.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".agent-preflight-stage-", dir=str(target)))
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    backups: dict[str, Path] = {}
    installed: list[str] = []

    try:
        for name in manifest["skills"]:
            shutil.copytree(source_root / name, staging / name)

        for name in manifest["skills"]:
            destination = destinations[name]
            if destination.exists() or destination.is_symlink():
                backup = backup_path(destination, timestamp)
                destination.replace(backup)
                backups[name] = backup
            (staging / name).replace(destination)
            installed.append(name)

        failures = {
            name: compare_skill(source_root / name, destinations[name])
            for name in manifest["skills"]
        }
        unhealthy = {name: item for name, item in failures.items() if item["status"] != "healthy"}
        if unhealthy:
            raise RuntimeError(f"post-install verification failed: {sorted(unhealthy)}")
        report["verified"] = True
        report["backups"] = {name: str(path) for name, path in backups.items()}
        return report
    except Exception:
        for name in reversed(installed):
            remove_path(destinations[name])
        for name, backup in backups.items():
            if backup.exists():
                backup.replace(destinations[name])
        raise
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def print_human(report: dict) -> None:
    verb = "Would install" if report["dry_run"] and report["ready"] else "Would refuse"
    if not report["dry_run"]:
        verb = "Installed"
    print(f"{verb} Agent Preflight {report['version']} -> {report['target']}")
    for name in report["skills"]:
        print(f"- {name}")
    for name, path in report["backups"].items():
        print(f"Backup: {name} -> {path}")
    if report["dry_run"]:
        if not report["ready"]:
            print("Existing skills require --force before installation can proceed.")
        print("Dry run only; no files changed.")
    elif report["verified"]:
        print("Installation verified.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, default=default_target(), help="destination skill root")
    parser.add_argument("--force", action="store_true", help="back up and replace existing skills")
    parser.add_argument("--dry-run", action="store_true", help="show the complete plan without writing")
    parser.add_argument("--json", action="store_true", help="emit a machine-readable report")
    args = parser.parse_args()

    try:
        report = install(args.target, force=args.force, dry_run=args.dry_run)
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"Installation refused: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
