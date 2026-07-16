#!/usr/bin/env python3
"""Validate and export behavior cases for model-based forward evaluation."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "evals" / "cases.jsonl"
VALID_MODES = {"DIRECT", "INSPECT", "CLARIFY", "DISCOVER", "GATE"}
VALID_ASK = {"none", "only_if_inspection_fails", "focused", "staged", "approval_only"}


def load_cases() -> list[dict]:
    cases: list[dict] = []
    for lineno, raw in enumerate(CASES.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        case = json.loads(raw)
        case["_line"] = lineno
        cases.append(case)
    return cases


def check(cases: list[dict]) -> list[str]:
    errors: list[str] = []
    ids: set[str] = set()
    for case in cases:
        prefix = f"line {case['_line']} ({case.get('id', 'missing-id')})"
        if case.get("id") in ids:
            errors.append(f"{prefix}: duplicate id")
        ids.add(case.get("id"))
        if case.get("expected_mode") not in VALID_MODES:
            errors.append(f"{prefix}: invalid expected_mode")
        if case.get("ask_policy") not in VALID_ASK:
            errors.append(f"{prefix}: invalid ask_policy")
        for field in ("expected_skills", "must_include", "prohibited_actions"):
            if not isinstance(case.get(field), list):
                errors.append(f"{prefix}: {field} must be a list")
        if not case.get("request", "").strip():
            errors.append(f"{prefix}: empty request")
    return errors


def export(cases: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for case in cases:
            prompt = {
                "id": case["id"],
                "prompt": (
                    "Use the Agent Preflight skill pack for the following user request. "
                    "Respond naturally, but append a final machine-readable line named "
                    "PREFLIGHT_EVAL_JSON containing mode, invoked_skills, questions_asked, "
                    "approval_requested, and actions_taken.\n\nUSER REQUEST:\n"
                    + case["request"]
                ),
            }
            handle.write(json.dumps(prompt, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate cases and print coverage")
    parser.add_argument("--export", type=Path, help="write prompts for an external model harness")
    args = parser.parse_args()

    cases = load_cases()
    errors = check(cases)
    if errors:
        print("Eval validation failed:")
        for item in errors:
            print(f"- {item}")
        return 1

    if args.export:
        export(cases, args.export)
        print(f"Exported {len(cases)} eval prompts to {args.export}")

    modes = Counter(case["expected_mode"] for case in cases)
    locales = Counter(case["locale"] for case in cases)
    categories = Counter(case["category"] for case in cases)
    print(f"Eval corpus valid: {len(cases)} cases")
    print("Modes: " + ", ".join(f"{k}={v}" for k, v in sorted(modes.items())))
    print("Locales: " + ", ".join(f"{k}={v}" for k, v in sorted(locales.items())))
    print("Categories: " + ", ".join(f"{k}={v}" for k, v in sorted(categories.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
