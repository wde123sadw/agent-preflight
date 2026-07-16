#!/usr/bin/env python3
"""Static validation for the Agent Preflight skill pack."""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

from packlib import MANIFEST, ROOT, load_manifest


SKILLS = ROOT / "skills"
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$")
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


def validate_links(path: Path, text: str, errors: list[str]) -> set[Path]:
    linked: set[Path] = set()
    for target in LINK_RE.findall(text):
        clean = target.strip().split("#", 1)[0]
        if not clean or "://" in clean or clean.startswith("mailto:"):
            continue
        resolved = (path.parent / clean).resolve()
        linked.add(resolved)
        if not resolved.exists():
            error(errors, f"{path}: broken local link {target!r}")
    return linked


def validate_manifest(manifest: dict, errors: list[str]) -> None:
    if manifest.get("schema_version") != 1:
        error(errors, f"{MANIFEST}: unsupported schema_version")
    if not SEMVER_RE.fullmatch(str(manifest.get("version", ""))):
        error(errors, f"{MANIFEST}: version must be semantic versioning")
    if not re.fullmatch(r"\d+\.\d+", str(manifest.get("minimum_python", ""))):
        error(errors, f"{MANIFEST}: minimum_python must use major.minor format")
    if set(manifest.get("modes", [])) != {"DIRECT", "INSPECT", "CLARIFY", "DISCOVER", "GATE"}:
        error(errors, f"{MANIFEST}: mode set does not match the routing protocol")
    if set(manifest.get("profiles", [])) != {"fast", "balanced", "deep", "critical"}:
        error(errors, f"{MANIFEST}: profile set does not match the routing protocol")
    for readme in (ROOT / "README.md", ROOT / "README.zh-CN.md"):
        if readme.exists() and f"v{manifest['version']}" not in readme.read_text(encoding="utf-8"):
            error(errors, f"{readme}: status does not mention v{manifest['version']}")


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
    linked = validate_links(skill_md, text, errors)

    refs_dir = skill_dir / "references"
    refs = list(refs_dir.glob("*.md")) if refs_dir.exists() else []
    if not refs:
        error(errors, f"{name}: references directory is empty")
    for ref in refs:
        ref_text = ref.read_text(encoding="utf-8")
        validate_links(ref, ref_text, errors)
        if "TODO" in ref_text:
            error(errors, f"{ref}: unresolved TODO")
        if ref.resolve() not in linked:
            error(errors, f"{ref}: reference is not linked directly from SKILL.md")

    forbidden = {"README.md", "CHANGELOG.md", "INSTALLATION_GUIDE.md", "QUICK_REFERENCE.md"}
    clutter = sorted(path.name for path in skill_dir.iterdir() if path.name in forbidden)
    if clutter:
        error(errors, f"{name}: skill contains project-level documentation {clutter}")

    if not openai_yaml.exists():
        error(errors, f"{name}: missing agents/openai.yaml")
    else:
        ui = openai_yaml.read_text(encoding="utf-8")
        for key in ("display_name:", "short_description:", "default_prompt:"):
            if key not in ui:
                error(errors, f"{openai_yaml}: missing {key}")
        if f"${name}" not in ui:
            error(errors, f"{openai_yaml}: default_prompt must mention ${name}")


def validate_evals(manifest: dict, errors: list[str]) -> int:
    path = ROOT / "evals" / "cases.jsonl"
    schema_path = ROOT / "evals" / "response.schema.json"
    ab_response_path = ROOT / "evals" / "ab-response.schema.json"
    ab_review_path = ROOT / "evals" / "ab-review.schema.json"
    ab_key_path = ROOT / "evals" / "ab-key.schema.json"
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
        if case.get("expected_mode") not in set(manifest["modes"]):
            error(errors, f"{path}:{lineno}: invalid expected_mode")
        unknown = set(case.get("expected_skills", [])) - set(manifest["skills"])
        if unknown:
            error(errors, f"{path}:{lineno}: unknown expected skills {sorted(unknown)}")
    if count < 60:
        error(errors, f"{path}: expected at least 60 behavior cases, found {count}")

    if not schema_path.exists():
        error(errors, "missing evals/response.schema.json")
    else:
        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            mode_enum = set(schema["properties"]["mode"]["enum"])
            skill_enum = set(schema["properties"]["invoked_skills"]["items"]["enum"])
            if mode_enum != set(manifest["modes"]):
                error(errors, f"{schema_path}: mode enum is out of sync with manifest")
            if skill_enum != set(manifest["skills"]):
                error(errors, f"{schema_path}: skill enum is out of sync with manifest")
        except (KeyError, TypeError, json.JSONDecodeError) as exc:
            error(errors, f"{schema_path}: invalid response schema: {exc}")

    for experiment_schema in (ab_response_path, ab_review_path, ab_key_path):
        if not experiment_schema.exists():
            error(errors, f"missing {experiment_schema.relative_to(ROOT)}")
            continue
        try:
            schema = json.loads(experiment_schema.read_text(encoding="utf-8"))
            if schema.get("type") != "object" or not schema.get("required"):
                error(errors, f"{experiment_schema}: schema must define an object and required fields")
        except json.JSONDecodeError as exc:
            error(errors, f"{experiment_schema}: invalid JSON schema: {exc}")

    if ab_review_path.exists():
        try:
            review_schema = json.loads(ab_review_path.read_text(encoding="utf-8"))
            dimensions = set(review_schema["$defs"]["scorecard"]["required"])
            expected_dimensions = {
                "task_success",
                "question_value",
                "self_service",
                "capability_discipline",
                "approval_safety",
                "context_efficiency",
            }
            if dimensions != expected_dimensions:
                error(errors, f"{ab_review_path}: review dimensions are out of sync with the A/B analyzer")
        except (KeyError, TypeError, json.JSONDecodeError) as exc:
            error(errors, f"{ab_review_path}: invalid review schema: {exc}")
    return count


def validate_python(errors: list[str]) -> int:
    paths = list((ROOT / "scripts").glob("*.py")) + list((ROOT / "tests").glob("test_*.py"))
    for path in paths:
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            error(errors, f"{path}: Python syntax error: {exc}")
    return len(paths)


def validate_project_files(errors: list[str]) -> None:
    required = [
        ROOT / "README.md",
        ROOT / "README.zh-CN.md",
        ROOT / "CHANGELOG.md",
        ROOT / "CONTRIBUTING.md",
        ROOT / "SECURITY.md",
        ROOT / "LICENSE",
        ROOT / ".github" / "workflows" / "ci.yml",
        ROOT / ".github" / "ISSUE_TEMPLATE" / "behavior-report.yml",
    ]
    for path in required:
        if not path.exists():
            error(errors, f"missing required project file: {path}")
    docs = [ROOT / "README.md", ROOT / "README.zh-CN.md", ROOT / "CONTRIBUTING.md"]
    docs += list((ROOT / "docs").glob("*.md")) + list((ROOT / "evals").glob("*.md"))
    for path in docs:
        if path.exists():
            validate_links(path, path.read_text(encoding="utf-8"), errors)

    workflow = ROOT / ".github" / "workflows" / "ci.yml"
    if workflow.exists():
        text = workflow.read_text(encoding="utf-8")
        for action in ("actions/checkout", "actions/setup-python"):
            if not re.search(rf"{re.escape(action)}@[0-9a-f]{{40}}", text):
                error(errors, f"{workflow}: {action} must be pinned to a full commit SHA")


def run_validation() -> tuple[list[str], dict]:
    errors: list[str] = []
    try:
        manifest = load_manifest()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [f"{MANIFEST}: {exc}"], {"skills": 0, "eval_cases": 0, "python_files": 0}
    validate_manifest(manifest, errors)
    validate_project_files(errors)
    expected = set(manifest["skills"])
    actual = {p.name for p in SKILLS.iterdir() if p.is_dir()} if SKILLS.exists() else set()
    if actual != expected:
        error(errors, f"skill set mismatch: missing={sorted(expected-actual)} extra={sorted(actual-expected)}")
    for name in sorted(expected & actual):
        validate_skill(SKILLS / name, errors)
    eval_count = validate_evals(manifest, errors)
    python_count = validate_python(errors)

    policy_text = "\n".join(path.read_text(encoding="utf-8") for path in SKILLS.rglob("*.md")).lower()
    for phrase in ("explicit approval", "discovery is not", "do not install"):
        if phrase not in policy_text:
            error(errors, f"pack is missing required approval concept: {phrase!r}")
    return errors, {"skills": len(expected), "eval_cases": eval_count, "python_files": python_count}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit a machine-readable validation report")
    args = parser.parse_args()
    errors, counts = run_validation()
    report = {"passed": not errors, **counts, "errors": errors}
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif errors:
        print("Agent Preflight validation failed:")
        for item in errors:
            print(f"- {item}")
    else:
        print(
            "Agent Preflight validation passed: "
            f"{counts['skills']} skills, {counts['eval_cases']} eval cases, "
            f"{counts['python_files']} Python files"
        )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
