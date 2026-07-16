#!/usr/bin/env python3
"""Static validation for the Agent Preflight skill pack."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
EXPECTED = {
    "using-agent-preflight",
    "intent-preflight",
    "capability-gap-analysis",
    "tool-discovery",
    "tool-review-gate",
    "context-budget",
}
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def error(errors: list[str], message: str) -> None:
    errors.append(message)


def parse_frontmatter(text: str, path: Path, errors: list[str]) -> dict[str, str]:
    if not text.startswith("---\n"):
        error(errors, f"{path}: missing opening YAML delimiter")
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        error(errors, f"{path}: missing closing YAML delimiter")
        return {}
    fields: dict[str, str] = {}
    for raw in text[4:end].splitlines():
        if not raw.strip():
            continue
        if ":" not in raw:
            error(errors, f"{path}: malformed frontmatter line: {raw!r}")
            continue
        key, value = raw.split(":", 1)
        fields[key.strip()] = value.strip()
    return fields


def validate_links(path: Path, text: str, errors: list[str]) -> None:
    for target in LINK_RE.findall(text):
        clean = target.strip().split("#", 1)[0]
        if not clean or "://" in clean or clean.startswith("mailto:"):
            continue
        resolved = (path.parent / clean).resolve()
        if not resolved.exists():
            error(errors, f"{path}: broken local link {target!r}")


def validate_skill(skill_dir: Path, errors: list[str]) -> None:
    name = skill_dir.name
    skill_md = skill_dir / "SKILL.md"
    openai_yaml = skill_dir / "agents" / "openai.yaml"

    if not skill_md.exists():
        error(errors, f"{name}: missing SKILL.md")
        return
    text = skill_md.read_text(encoding="utf-8")
    fields = parse_frontmatter(text, skill_md, errors)
    if set(fields) != {"name", "description"}:
        error(errors, f"{skill_md}: frontmatter must contain only name and description")
    if fields.get("name") != name:
        error(errors, f"{skill_md}: name does not match folder")
    if len(fields.get("description", "")) < 80:
        error(errors, f"{skill_md}: description is too short to trigger reliably")
    if "TODO" in text or "[TODO" in text:
        error(errors, f"{skill_md}: unresolved TODO")
    if len(text.splitlines()) > 500:
        error(errors, f"{skill_md}: exceeds 500-line progressive-disclosure limit")
    validate_links(skill_md, text, errors)

    refs = list((skill_dir / "references").glob("*.md"))
    if not refs:
        error(errors, f"{name}: references directory is empty")
    for ref in refs:
        ref_text = ref.read_text(encoding="utf-8")
        validate_links(ref, ref_text, errors)
        if "TODO" in ref_text:
            error(errors, f"{ref}: unresolved TODO")

    if not openai_yaml.exists():
        error(errors, f"{name}: missing agents/openai.yaml")
    else:
        ui = openai_yaml.read_text(encoding="utf-8")
        for key in ("display_name:", "short_description:", "default_prompt:"):
            if key not in ui:
                error(errors, f"{openai_yaml}: missing {key}")
        if f"${name}" not in ui:
            error(errors, f"{openai_yaml}: default_prompt must mention ${name}")


def validate_evals(errors: list[str]) -> int:
    path = ROOT / "evals" / "cases.jsonl"
    if not path.exists():
        error(errors, "missing evals/cases.jsonl")
        return 0
    count = 0
    ids: set[str] = set()
    required = {
        "id",
        "locale",
        "category",
        "request",
        "expected_mode",
        "expected_skills",
        "ask_policy",
        "must_include",
        "prohibited_actions",
        "rationale",
    }
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        count += 1
        try:
            case = json.loads(raw)
        except json.JSONDecodeError as exc:
            error(errors, f"{path}:{lineno}: invalid JSON: {exc}")
            continue
        missing = required - set(case)
        if missing:
            error(errors, f"{path}:{lineno}: missing fields {sorted(missing)}")
        case_id = case.get("id")
        if case_id in ids:
            error(errors, f"{path}:{lineno}: duplicate id {case_id!r}")
        ids.add(case_id)
        if case.get("expected_mode") not in {"DIRECT", "INSPECT", "CLARIFY", "DISCOVER", "GATE"}:
            error(errors, f"{path}:{lineno}: invalid expected_mode")
        unknown = set(case.get("expected_skills", [])) - EXPECTED
        if unknown:
            error(errors, f"{path}:{lineno}: unknown expected skills {sorted(unknown)}")
    if count < 24:
        error(errors, f"{path}: expected at least 24 behavior cases, found {count}")
    return count


def main() -> int:
    errors: list[str] = []
    actual = {p.name for p in SKILLS.iterdir() if p.is_dir()} if SKILLS.exists() else set()
    if actual != EXPECTED:
        error(errors, f"skill set mismatch: missing={sorted(EXPECTED-actual)} extra={sorted(actual-EXPECTED)}")
    for name in sorted(EXPECTED & actual):
        validate_skill(SKILLS / name, errors)
    eval_count = validate_evals(errors)

    policy_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in SKILLS.rglob("*.md")
    ).lower()
    for phrase in ("explicit approval", "discovery is not", "do not install"):
        if phrase not in policy_text:
            error(errors, f"pack is missing required approval concept: {phrase!r}")

    if errors:
        print("Agent Preflight validation failed:")
        for item in errors:
            print(f"- {item}")
        return 1

    print(f"Agent Preflight validation passed: {len(EXPECTED)} skills, {eval_count} eval cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
