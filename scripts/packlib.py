#!/usr/bin/env python3
"""Shared manifest and integrity helpers for Agent Preflight scripts."""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "agent-preflight.json"
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def load_manifest(path: Path = MANIFEST) -> dict[str, Any]:
    """Load and minimally validate the pack manifest."""
    data = json.loads(path.read_text(encoding="utf-8"))
    required = {"schema_version", "name", "version", "minimum_python", "skills", "modes", "profiles"}
    missing = required - set(data)
    if missing:
        raise ValueError(f"manifest missing fields: {sorted(missing)}")
    if data["name"] != "agent-preflight":
        raise ValueError("manifest name must be agent-preflight")
    if not isinstance(data["skills"], list) or not data["skills"]:
        raise ValueError("manifest skills must be a non-empty list")
    if len(data["skills"]) != len(set(data["skills"])):
        raise ValueError("manifest skills must be unique")
    invalid = [name for name in data["skills"] if not isinstance(name, str) or not SKILL_NAME_RE.fullmatch(name)]
    if invalid:
        raise ValueError(f"manifest contains invalid skill names: {invalid}")
    return data


def default_target() -> Path:
    """Return the default Codex skill root without mutating it."""
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    return codex_home / "skills"


def file_hashes(root: Path) -> dict[str, str]:
    """Return content hashes for files in a skill directory."""
    result: dict[str, str] = {}
    if not root.is_dir():
        return result
    for path in sorted(root.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        relative = path.relative_to(root).as_posix()
        result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def compare_skill(source: Path, destination: Path) -> dict[str, Any]:
    """Compare an installed skill with its source copy."""
    if not destination.is_dir():
        return {
            "status": "missing",
            "missing_files": sorted(file_hashes(source)),
            "extra_files": [],
            "changed_files": [],
        }
    source_files = file_hashes(source)
    target_files = file_hashes(destination)
    missing = sorted(source_files.keys() - target_files.keys())
    extra = sorted(target_files.keys() - source_files.keys())
    changed = sorted(
        path for path in source_files.keys() & target_files.keys()
        if source_files[path] != target_files[path]
    )
    status = "healthy" if not (missing or extra or changed) else "modified"
    return {
        "status": status,
        "missing_files": missing,
        "extra_files": extra,
        "changed_files": changed,
    }
