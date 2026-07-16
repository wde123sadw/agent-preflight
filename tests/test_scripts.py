from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import doctor  # noqa: E402
import install as installer  # noqa: E402
import packlib  # noqa: E402
import run_evals  # noqa: E402
import validate_pack  # noqa: E402


def valid_trace(case: dict) -> dict:
    question_counts = {
        "none": 0,
        "only_if_inspection_fails": 0,
        "focused": 1,
        "staged": 1,
        "approval_only": 1,
    }
    return {
        "mode": case["expected_mode"],
        "invoked_skills": case["expected_skills"],
        "questions_asked": ["Material decision?"] * question_counts[case["ask_policy"]],
        "approval_requested": case["expected_mode"] == "GATE",
        "external_effects_executed": False,
    }


class ManifestTests(unittest.TestCase):
    def test_manifest_matches_source_directories(self) -> None:
        manifest = packlib.load_manifest()
        actual = {path.name for path in (ROOT / "skills").iterdir() if path.is_dir()}
        self.assertEqual(set(manifest["skills"]), actual)
        self.assertEqual(manifest["version"], "0.2.0")

    def test_pack_validator_passes(self) -> None:
        errors, counts = validate_pack.run_validation()
        self.assertEqual(errors, [])
        self.assertEqual(counts["skills"], 6)
        self.assertGreaterEqual(counts["eval_cases"], 36)


class EvalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cases = run_evals.load_cases()

    def write_responses(self, path: Path, mutate=None) -> None:
        lines = []
        for case in self.cases:
            trace = valid_trace(case)
            if mutate:
                mutate(case, trace)
            lines.append(json.dumps({"id": case["id"], "preflight": trace}, ensure_ascii=False))
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def test_extracts_trace_from_output_line(self) -> None:
        trace = valid_trace(self.cases[0])
        record = {
            "id": self.cases[0]["id"],
            "output": "Natural response.\nPREFLIGHT_EVAL_JSON: " + json.dumps(trace),
        }
        self.assertEqual(run_evals.extract_trace(record), trace)

    def test_perfect_corpus_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "responses.jsonl"
            self.write_responses(path)
            report = run_evals.load_and_score(self.cases, path, 10.0, 0.90)
        self.assertTrue(report["passed"])
        self.assertEqual(report["summary"]["average_score"], 12.0)
        self.assertEqual(report["summary"]["mode_accuracy"], 1.0)

    def test_cli_exports_and_scores_a_complete_corpus(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            prompts = temp_root / "prompts.jsonl"
            responses = temp_root / "responses.jsonl"
            self.write_responses(responses)
            exported = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "run_evals.py"), "--export", str(prompts)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            scored = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "run_evals.py"), "--score", str(responses)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            prompt_count = len(prompts.read_text(encoding="utf-8").splitlines())
        self.assertEqual(exported.returncode, 0, exported.stderr)
        self.assertEqual(prompt_count, len(self.cases))
        self.assertEqual(scored.returncode, 0, scored.stderr)
        self.assertIn("Eval score: PASS", scored.stdout)

    def test_wrong_mode_fails_threshold(self) -> None:
        first_id = self.cases[0]["id"]

        def mutate(case: dict, trace: dict) -> None:
            if case["id"] == first_id:
                trace["mode"] = "GATE"

        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "responses.jsonl"
            self.write_responses(path, mutate)
            report = run_evals.load_and_score(self.cases, path, 10.0, 1.0)
        self.assertFalse(report["passed"])
        self.assertLess(report["summary"]["mode_accuracy"], 1.0)

    def test_gated_external_effect_is_hard_failure(self) -> None:
        gate_id = next(case["id"] for case in self.cases if case["expected_mode"] == "GATE")

        def mutate(case: dict, trace: dict) -> None:
            if case["id"] == gate_id:
                trace["external_effects_executed"] = True

        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "responses.jsonl"
            self.write_responses(path, mutate)
            report = run_evals.load_and_score(self.cases, path, 0.0, 0.0)
        self.assertFalse(report["passed"])
        self.assertEqual(report["hard_failure_ids"], [gate_id])

    def test_missing_response_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "responses.jsonl"
            case = self.cases[0]
            path.write_text(
                json.dumps({"id": case["id"], "preflight": valid_trace(case)}) + "\n",
                encoding="utf-8",
            )
            report = run_evals.load_and_score(self.cases, path, 0.0, 0.0)
        self.assertFalse(report["passed"])
        self.assertEqual(report["summary"]["missing_responses"], len(self.cases) - 1)

    def test_question_budget_penalizes_interview_on_direct_task(self) -> None:
        self.assertEqual(run_evals.question_score("none", 0), 2.0)
        self.assertEqual(run_evals.question_score("none", 1), 0.0)
        self.assertEqual(run_evals.question_score("focused", 3), 2.0)
        self.assertEqual(run_evals.question_score("focused", 8), 0.0)


class InstallationTests(unittest.TestCase):
    def test_dry_run_does_not_create_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "skills"
            report = installer.install(target, dry_run=True)
            self.assertFalse(target.exists())
            self.assertTrue(report["dry_run"])
            self.assertFalse(report["verified"])

    def test_dry_run_reports_collisions_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "skills"
            existing = target / "intent-preflight"
            existing.mkdir(parents=True)
            marker = existing / "owned-by-user.txt"
            marker.write_text("keep", encoding="utf-8")
            report = installer.install(target, dry_run=True)
            self.assertFalse(report["ready"])
            self.assertEqual(report["collisions"], ["intent-preflight"])
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep")

    def test_install_and_doctor(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "skills"
            report = installer.install(target)
            health = doctor.inspect_installation(target)
            self.assertTrue(report["verified"])
            self.assertTrue(health["healthy"])
            self.assertEqual(health["summary"]["healthy"], 6)

    def test_collision_refuses_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "skills"
            existing = target / "intent-preflight"
            existing.mkdir(parents=True)
            marker = existing / "owned-by-user.txt"
            marker.write_text("keep", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                installer.install(target)
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep")
            self.assertEqual({path.name for path in target.iterdir()}, {"intent-preflight"})

    def test_force_keeps_backups(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "skills"
            installer.install(target)
            modified = target / "intent-preflight" / "SKILL.md"
            modified.write_text("local change", encoding="utf-8")
            report = installer.install(target, force=True)
            backup = Path(report["backups"]["intent-preflight"])
            self.assertEqual((backup / "SKILL.md").read_text(encoding="utf-8"), "local change")
            self.assertTrue(doctor.inspect_installation(target)["healthy"])

    def test_failed_force_install_restores_every_replaced_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "skills"
            installer.install(target)
            first = target / "using-agent-preflight" / "SKILL.md"
            second = target / "intent-preflight" / "SKILL.md"
            first.write_text("first local change", encoding="utf-8")
            second.write_text("second local change", encoding="utf-8")
            original_replace = Path.replace

            def fail_on_second_stage(path: Path, destination: Path):
                if path.name == "intent-preflight" and path.parent.name.startswith(".agent-preflight-stage-"):
                    raise OSError("simulated install failure")
                return original_replace(path, destination)

            with mock.patch.object(Path, "replace", fail_on_second_stage):
                with self.assertRaises(OSError):
                    installer.install(target, force=True)
            self.assertEqual(first.read_text(encoding="utf-8"), "first local change")
            self.assertEqual(second.read_text(encoding="utf-8"), "second local change")

    def test_doctor_detects_changed_and_extra_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "skills"
            installer.install(target)
            skill = target / "context-budget"
            (skill / "SKILL.md").write_text("changed", encoding="utf-8")
            (skill / "extra.txt").write_text("extra", encoding="utf-8")
            health = doctor.inspect_installation(target)
            result = health["skills"]["context-budget"]
            self.assertFalse(health["healthy"])
            self.assertEqual(result["status"], "modified")
            self.assertIn("SKILL.md", result["changed_files"])
            self.assertIn("extra.txt", result["extra_files"])


if __name__ == "__main__":
    unittest.main()
