#!/usr/bin/env python3
"""Check whether an Agent Preflight installation matches this release."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from packlib import ROOT, compare_skill, default_target, load_manifest


def inspect_installation(target: Path) -> dict:
    manifest = load_manifest()
    source_root = ROOT / "skills"
    target = target.expanduser().resolve()
    results = {
        name: compare_skill(source_root / name, target / name)
        for name in manifest["skills"]
    }
    healthy = sum(item["status"] == "healthy" for item in results.values())
    return {
        "pack": manifest["name"],
        "version": manifest["version"],
        "target": str(target),
        "healthy": healthy == len(results),
        "summary": {
            "healthy": healthy,
            "modified": sum(item["status"] == "modified" for item in results.values()),
            "missing": sum(item["status"] == "missing" for item in results.values()),
            "total": len(results),
        },
        "skills": results,
    }


def print_human(report: dict) -> None:
    state = "healthy" if report["healthy"] else "needs attention"
    print(f"Agent Preflight {report['version']}: {state}")
    print(f"Target: {report['target']}")
    for name, result in report["skills"].items():
        print(f"- {name}: {result['status']}")
        for field, label in (
            ("missing_files", "missing"),
            ("extra_files", "extra"),
            ("changed_files", "changed"),
        ):
            if result[field]:
                preview = ", ".join(result[field][:5])
                suffix = " ..." if len(result[field]) > 5 else ""
                print(f"  {label}: {preview}{suffix}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, default=default_target(), help="installed skill root")
    parser.add_argument("--json", action="store_true", help="emit a machine-readable report")
    args = parser.parse_args()

    try:
        report = inspect_installation(args.target)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Doctor failed: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human(report)
    return 0 if report["healthy"] else 1


if __name__ == "__main__":
    sys.exit(main())
