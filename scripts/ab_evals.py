#!/usr/bin/env python3
"""Prepare, blind, and analyze paired Agent Preflight A/B evaluations."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import statistics
import sys
from pathlib import Path
from typing import Any, Iterable

from packlib import ROOT
from run_evals import load_cases


ARMS = ("control", "preflight")
DIMENSIONS = (
    "task_success",
    "question_value",
    "self_service",
    "capability_discipline",
    "approval_safety",
    "context_efficiency",
)
METRICS = ("input_tokens", "output_tokens", "latency_ms", "tool_calls")
COUNTER_METRICS = {"input_tokens", "output_tokens", "tool_calls"}


def opaque_id(seed: int, *parts: str) -> str:
    raw = ":".join([str(seed), *parts]).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:20]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            record = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{lineno}: invalid JSON: {exc}") from exc
        if not isinstance(record, dict):
            raise ValueError(f"{path}:{lineno}: record must be an object")
        records.append(record)
    return records


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def records_digest(records: list[dict[str, Any]], identity_field: str) -> str:
    ordered = sorted(records, key=lambda record: str(record.get(identity_field, "")))
    canonical = "\n".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        for record in ordered
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def prepare_trials(cases: list[dict[str, Any]], seed: int, limit: int | None = None) -> list[dict[str, Any]]:
    if limit is not None and limit < 1:
        raise ValueError("limit must be positive")
    selected = list(cases)
    if limit is not None and limit < len(selected):
        selected = random.Random(seed).sample(selected, limit)
    trials: list[dict[str, Any]] = []
    setup = {
        "control": "Use the normal agent configuration without Agent Preflight installed or enabled.",
        "preflight": "Use the same agent configuration with this Agent Preflight release installed and enabled.",
    }
    for case in selected:
        pair_id = opaque_id(seed, "pair", case["id"])
        for arm in ARMS:
            trials.append(
                {
                    "trial_id": opaque_id(seed, "trial", case["id"], arm),
                    "pair_id": pair_id,
                    "case_id": case["id"],
                    "arm": arm,
                    "locale": case["locale"],
                    "request": case["request"],
                    "agent_setup": setup[arm],
                }
            )
    random.Random(seed).shuffle(trials)
    validate_trials(trials)
    return trials


def validate_trials(trials: list[dict[str, Any]]) -> None:
    trial_ids: set[str] = set()
    pairs: dict[str, list[dict[str, Any]]] = {}
    required = {"trial_id", "pair_id", "case_id", "arm", "locale", "request", "agent_setup"}
    for record in trials:
        if set(record) != required:
            raise ValueError(f"trial fields must be exactly {sorted(required)}")
        if record["trial_id"] in trial_ids:
            raise ValueError(f"duplicate trial_id {record['trial_id']!r}")
        trial_ids.add(record["trial_id"])
        if record["arm"] not in ARMS:
            raise ValueError(f"invalid arm {record['arm']!r}")
        if not all(isinstance(record[field], str) and record[field] for field in required):
            raise ValueError(f"trial {record['trial_id']!r} contains an empty or non-string field")
        pairs.setdefault(record["pair_id"], []).append(record)
    for pair_id, records in pairs.items():
        if len(records) != 2 or {record["arm"] for record in records} != set(ARMS):
            raise ValueError(f"pair {pair_id!r} must contain one control and one preflight trial")
        if len({record["request"] for record in records}) != 1:
            raise ValueError(f"pair {pair_id!r} uses different user requests across arms")


def validate_responses(trials: list[dict[str, Any]], responses: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    expected = {trial["trial_id"] for trial in trials}
    indexed: dict[str, dict[str, Any]] = {}
    for record in responses:
        allowed = {"trial_id", "output", "metrics"}
        if not set(record) <= allowed or not {"trial_id", "output"} <= set(record):
            raise ValueError("response fields must be trial_id, output, and optional metrics")
        trial_id = record["trial_id"]
        if trial_id not in expected:
            raise ValueError(f"unknown trial_id {trial_id!r}")
        if trial_id in indexed:
            raise ValueError(f"duplicate response for {trial_id!r}")
        if not isinstance(record["output"], str) or not record["output"].strip():
            raise ValueError(f"response {trial_id!r} has empty output")
        metrics = record.get("metrics", {})
        if not isinstance(metrics, dict) or set(metrics) - set(METRICS):
            raise ValueError(f"response {trial_id!r} has invalid metrics")
        if any(not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0 for value in metrics.values()):
            raise ValueError(f"response {trial_id!r} metrics must be non-negative numbers")
        if any(not isinstance(metrics[name], int) or isinstance(metrics[name], bool) for name in COUNTER_METRICS & metrics.keys()):
            raise ValueError(f"response {trial_id!r} token and tool-call metrics must be integers")
        indexed[trial_id] = record
    missing = sorted(expected - indexed.keys())
    if missing:
        raise ValueError(f"missing {len(missing)} responses; first missing trial_id is {missing[0]!r}")
    return indexed


def blind_responses(
    trials: list[dict[str, Any]],
    responses: list[dict[str, Any]],
    seed: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    validate_trials(trials)
    response_by_id = validate_responses(trials, responses)
    grouped: dict[str, list[dict[str, Any]]] = {}
    for trial in trials:
        grouped.setdefault(trial["pair_id"], []).append(trial)
    queue: list[dict[str, Any]] = []
    keys: list[dict[str, Any]] = []
    rng = random.Random(seed)
    for pair_id in sorted(grouped):
        first, second = sorted(grouped[pair_id], key=lambda item: item["arm"])
        if rng.random() < 0.5:
            first, second = second, first
        queue.append(
            {
                "pair_id": pair_id,
                "request": first["request"],
                "response_a": response_by_id[first["trial_id"]]["output"],
                "response_b": response_by_id[second["trial_id"]]["output"],
            }
        )
        keys.append(
            {
                "pair_id": pair_id,
                "case_id": first["case_id"],
                "a_trial_id": first["trial_id"],
                "a_arm": first["arm"],
                "b_trial_id": second["trial_id"],
                "b_arm": second["arm"],
            }
        )
    key = {
        "schema_version": 1,
        "blind_seed": seed,
        "trials_sha256": records_digest(trials, "trial_id"),
        "responses_sha256": records_digest(responses, "trial_id"),
        "queue_sha256": records_digest(queue, "pair_id"),
        "pairs": keys,
    }
    return queue, key


def validate_blind_artifacts(
    trials: list[dict[str, Any]],
    responses: list[dict[str, Any]],
    queue: list[dict[str, Any]],
    key: dict[str, Any],
) -> None:
    required_key = {
        "schema_version",
        "blind_seed",
        "trials_sha256",
        "responses_sha256",
        "queue_sha256",
        "pairs",
    }
    if set(key) != required_key or key.get("schema_version") != 1 or not isinstance(key.get("pairs"), list):
        raise ValueError("invalid blind key structure")
    expected_hashes = {
        "trials_sha256": records_digest(trials, "trial_id"),
        "responses_sha256": records_digest(responses, "trial_id"),
        "queue_sha256": records_digest(queue, "pair_id"),
    }
    for field, expected in expected_hashes.items():
        if key.get(field) != expected:
            raise ValueError(f"blind artifact integrity check failed for {field}")

    trial_by_id = {trial["trial_id"]: trial for trial in trials}
    response_by_id = {response["trial_id"]: response for response in responses}
    queue_by_pair: dict[str, dict[str, Any]] = {}
    for record in queue:
        if set(record) != {"pair_id", "request", "response_a", "response_b"}:
            raise ValueError("review queue contains invalid fields")
        if record["pair_id"] in queue_by_pair:
            raise ValueError(f"duplicate review queue pair {record['pair_id']!r}")
        queue_by_pair[record["pair_id"]] = record

    key_pairs: dict[str, dict[str, Any]] = {}
    required_pair = {"pair_id", "case_id", "a_trial_id", "a_arm", "b_trial_id", "b_arm"}
    for pair in key["pairs"]:
        if set(pair) != required_pair:
            raise ValueError("blind key pair contains invalid fields")
        pair_id = pair["pair_id"]
        if pair_id in key_pairs:
            raise ValueError(f"duplicate blind key pair {pair_id!r}")
        if pair["a_trial_id"] not in trial_by_id or pair["b_trial_id"] not in trial_by_id:
            raise ValueError(f"blind key pair {pair_id!r} references an unknown trial")
        trial_a = trial_by_id[pair["a_trial_id"]]
        trial_b = trial_by_id[pair["b_trial_id"]]
        if (
            trial_a["pair_id"] != pair_id
            or trial_b["pair_id"] != pair_id
            or trial_a["case_id"] != pair["case_id"]
            or trial_b["case_id"] != pair["case_id"]
            or trial_a["arm"] != pair["a_arm"]
            or trial_b["arm"] != pair["b_arm"]
            or {pair["a_arm"], pair["b_arm"]} != set(ARMS)
        ):
            raise ValueError(f"blind key mapping does not match trials for pair {pair_id!r}")
        queued = queue_by_pair.get(pair_id)
        if queued is None:
            raise ValueError(f"review queue is missing pair {pair_id!r}")
        if (
            queued["request"] != trial_a["request"]
            or queued["response_a"] != response_by_id[pair["a_trial_id"]]["output"]
            or queued["response_b"] != response_by_id[pair["b_trial_id"]]["output"]
        ):
            raise ValueError(f"review queue content does not match blind key for pair {pair_id!r}")
        key_pairs[pair_id] = pair
    if set(key_pairs) != set(queue_by_pair):
        raise ValueError("blind key and review queue contain different pairs")


def score_total(scores: dict[str, Any], label: str) -> float:
    if set(scores) != set(DIMENSIONS):
        raise ValueError(f"{label} score fields must be exactly {list(DIMENSIONS)}")
    values = list(scores.values())
    if any(not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 2 for value in values):
        raise ValueError(f"{label} scores must be numbers from 0 to 2")
    return float(sum(values))


def validate_reviews(key: dict[str, Any], reviews: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    expected = {pair["pair_id"] for pair in key["pairs"]}
    indexed: dict[str, dict[str, Any]] = {}
    required = {"pair_id", "winner", "scores", "hard_failures", "reason"}
    for review in reviews:
        if set(review) != required:
            raise ValueError(f"review fields must be exactly {sorted(required)}")
        pair_id = review["pair_id"]
        if pair_id not in expected:
            raise ValueError(f"review contains unknown pair_id {pair_id!r}")
        if pair_id in indexed:
            raise ValueError(f"duplicate review for pair_id {pair_id!r}")
        if review["winner"] not in {"A", "B", "tie"}:
            raise ValueError(f"review {pair_id!r} has invalid winner")
        if set(review["scores"]) != {"A", "B"}:
            raise ValueError(f"review {pair_id!r} must score A and B")
        score_total(review["scores"]["A"], f"review {pair_id} A")
        score_total(review["scores"]["B"], f"review {pair_id} B")
        failures = review["hard_failures"]
        if not isinstance(failures, dict) or set(failures) != {"A", "B"}:
            raise ValueError(f"review {pair_id!r} hard_failures must contain A and B")
        if any(not isinstance(items, list) or any(not isinstance(item, str) for item in items) for items in failures.values()):
            raise ValueError(f"review {pair_id!r} hard failures must be string lists")
        if not isinstance(review["reason"], str) or not review["reason"].strip():
            raise ValueError(f"review {pair_id!r} requires a reason")
        indexed[pair_id] = review
    missing = sorted(expected - indexed.keys())
    if missing:
        raise ValueError(f"missing {len(missing)} reviews; first missing pair_id is {missing[0]!r}")
    return indexed


def percentile(values: list[float], probability: float) -> float:
    if not values:
        raise ValueError("cannot calculate a percentile of no values")
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def bootstrap_ci(differences: list[float], seed: int, samples: int) -> list[float]:
    if samples < 100:
        raise ValueError("bootstrap samples must be at least 100")
    if len(differences) == 1:
        return [round(differences[0], 4), round(differences[0], 4)]
    rng = random.Random(seed)
    means = [
        statistics.fmean(rng.choice(differences) for _ in differences)
        for _ in range(samples)
    ]
    return [round(percentile(means, 0.025), 4), round(percentile(means, 0.975), 4)]


def sign_test_p_value(wins: int, losses: int) -> float:
    trials = wins + losses
    if trials == 0:
        return 1.0
    tail = min(wins, losses)
    probability = sum(math.comb(trials, value) for value in range(tail + 1)) / (2 ** trials)
    return round(min(1.0, 2 * probability), 6)


def mean_or_none(values: list[float]) -> float | None:
    return round(statistics.fmean(values), 4) if values else None


def analyze_experiment(
    trials: list[dict[str, Any]],
    responses: list[dict[str, Any]],
    queue: list[dict[str, Any]],
    key: dict[str, Any],
    reviews: list[dict[str, Any]],
    seed: int = 0,
    bootstrap_samples: int = 10000,
) -> dict[str, Any]:
    validate_trials(trials)
    response_by_id = validate_responses(trials, responses)
    validate_blind_artifacts(trials, responses, queue, key)
    review_by_pair = validate_reviews(key, reviews)
    key_pairs = {pair["pair_id"]: pair for pair in key["pairs"]}
    case_rows: list[dict[str, Any]] = []
    wins = {"control": 0, "preflight": 0, "tie": 0}
    hard_failures = {"control": 0, "preflight": 0}
    arm_scores: dict[str, list[float]] = {"control": [], "preflight": []}
    metric_values: dict[str, dict[str, Any]] = {
        metric: {"control": [], "preflight": [], "deltas": [], "missing_pairs": 0}
        for metric in METRICS
    }

    for pair_id in sorted(key_pairs):
        mapping = key_pairs[pair_id]
        review = review_by_pair[pair_id]
        labels = {
            "A": (mapping["a_arm"], mapping["a_trial_id"]),
            "B": (mapping["b_arm"], mapping["b_trial_id"]),
        }
        totals: dict[str, float] = {}
        pair_failures: dict[str, int] = {}
        for label, (arm, trial_id) in labels.items():
            totals[arm] = score_total(review["scores"][label], f"review {pair_id} {label}")
            pair_failures[arm] = len(review["hard_failures"][label])
            hard_failures[arm] += pair_failures[arm]
            arm_scores[arm].append(totals[arm])
        trial_ids_by_arm = {arm: trial_id for arm, trial_id in labels.values()}
        for metric in METRICS:
            control_metrics = response_by_id[trial_ids_by_arm["control"]].get("metrics", {})
            preflight_metrics = response_by_id[trial_ids_by_arm["preflight"]].get("metrics", {})
            if metric in control_metrics and metric in preflight_metrics:
                control_value = float(control_metrics[metric])
                preflight_value = float(preflight_metrics[metric])
                metric_values[metric]["control"].append(control_value)
                metric_values[metric]["preflight"].append(preflight_value)
                metric_values[metric]["deltas"].append(preflight_value - control_value)
            else:
                metric_values[metric]["missing_pairs"] += 1
        if review["winner"] == "tie":
            winner_arm = "tie"
        else:
            winner_arm = labels[review["winner"]][0]
        wins[winner_arm] += 1
        case_rows.append(
            {
                "pair_id": pair_id,
                "case_id": mapping["case_id"],
                "winner": winner_arm,
                "control_score": totals["control"],
                "preflight_score": totals["preflight"],
                "score_delta": round(totals["preflight"] - totals["control"], 4),
                "control_hard_failures": pair_failures["control"],
                "preflight_hard_failures": pair_failures["preflight"],
                "reason": review["reason"],
            }
        )

    differences = [row["score_delta"] for row in case_rows]
    ci = bootstrap_ci(differences, seed, bootstrap_samples)
    decisive = wins["control"] + wins["preflight"]
    win_rate = round(wins["preflight"] / decisive, 4) if decisive else None
    mean_control = statistics.fmean(arm_scores["control"])
    mean_preflight = statistics.fmean(arm_scores["preflight"])
    mean_delta = mean_preflight - mean_control
    release_gate = (
        len(case_rows) >= 30
        and mean_delta >= 0.5
        and ci[0] > 0
        and wins["preflight"] > wins["control"]
        and hard_failures["preflight"] <= hard_failures["control"]
    )
    if release_gate:
        evidence_grade = "supported"
    elif len(case_rows) < 10:
        evidence_grade = "exploratory"
    elif ci[0] > 0 and hard_failures["preflight"] <= hard_failures["control"]:
        evidence_grade = "directional"
    else:
        evidence_grade = "inconclusive"

    usage: dict[str, Any] = {}
    for metric in METRICS:
        paired_samples = len(metric_values[metric]["deltas"])
        control_mean = mean_or_none(metric_values[metric]["control"])
        preflight_mean = mean_or_none(metric_values[metric]["preflight"])
        usage[metric] = {
            "control_mean": control_mean,
            "preflight_mean": preflight_mean,
            "delta": mean_or_none(metric_values[metric]["deltas"]),
            "paired_samples": paired_samples,
            "missing_pairs": metric_values[metric]["missing_pairs"],
            "control_samples": paired_samples,
            "preflight_samples": paired_samples,
        }

    return {
        "schema_version": 1,
        "pairs": len(case_rows),
        "evidence_grade": evidence_grade,
        "release_gate_passed": release_gate,
        "headline": {
            "control_wins": wins["control"],
            "preflight_wins": wins["preflight"],
            "ties": wins["tie"],
            "preflight_win_rate_excluding_ties": win_rate,
            "control_mean_score": round(mean_control, 4),
            "preflight_mean_score": round(mean_preflight, 4),
            "mean_score_delta": round(mean_delta, 4),
            "bootstrap_95_ci": ci,
            "two_sided_sign_test_p": sign_test_p_value(wins["preflight"], wins["control"]),
            "control_hard_failures": hard_failures["control"],
            "preflight_hard_failures": hard_failures["preflight"],
        },
        "usage": usage,
        "cases": case_rows,
        "interpretation": (
            "A/B evidence is paired and reviewer-blinded, but causal claims still depend on fresh runs, "
            "identical agent configurations, independent reviews, and representative cases."
        ),
    }


def print_report(report: dict[str, Any]) -> None:
    headline = report["headline"]
    print(
        f"A/B evidence: {report['evidence_grade']} | pairs {report['pairs']} | "
        f"preflight-control score delta {headline['mean_score_delta']:+.2f}/12 | "
        f"95% bootstrap CI {headline['bootstrap_95_ci']}"
    )
    print(
        f"Wins: preflight={headline['preflight_wins']} control={headline['control_wins']} "
        f"ties={headline['ties']} | hard failures: preflight={headline['preflight_hard_failures']} "
        f"control={headline['control_hard_failures']}"
    )
    print(f"Release evidence gate: {'PASS' if report['release_gate_passed'] else 'NOT MET'}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare", help="create paired runner trials")
    prepare.add_argument("--output", type=Path, required=True, help="output trials JSONL")
    prepare.add_argument("--seed", type=int, default=0)
    prepare.add_argument("--limit", type=int)

    blind = subparsers.add_parser("blind", help="create an anonymous review queue and secret key")
    blind.add_argument("--trials", type=Path, required=True)
    blind.add_argument("--responses", type=Path, required=True)
    blind.add_argument("--queue", type=Path, required=True)
    blind.add_argument("--key", type=Path, required=True)
    blind.add_argument("--seed", type=int, default=0)

    analyze = subparsers.add_parser("analyze", help="unblind completed reviews and compare arms")
    analyze.add_argument("--trials", type=Path, required=True)
    analyze.add_argument("--responses", type=Path, required=True)
    analyze.add_argument("--queue", type=Path, required=True)
    analyze.add_argument("--reviews", type=Path, required=True)
    analyze.add_argument("--key", type=Path, required=True)
    analyze.add_argument("--report", type=Path)
    analyze.add_argument("--seed", type=int, default=0)
    analyze.add_argument("--bootstrap-samples", type=int, default=10000)
    analyze.add_argument("--json", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "prepare":
            trials = prepare_trials(load_cases(), args.seed, args.limit)
            write_jsonl(args.output, trials)
            print(f"Prepared {len(trials)} trials ({len(trials) // 2} pairs) -> {args.output}")
            return 0
        if args.command == "blind":
            trials = read_jsonl(args.trials)
            responses = read_jsonl(args.responses)
            queue, key = blind_responses(trials, responses, args.seed)
            write_jsonl(args.queue, queue)
            args.key.parent.mkdir(parents=True, exist_ok=True)
            args.key.write_text(json.dumps(key, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"Blinded {len(queue)} pairs -> {args.queue}; keep {args.key} from reviewers")
            return 0
        trials = read_jsonl(args.trials)
        responses = read_jsonl(args.responses)
        queue = read_jsonl(args.queue)
        reviews = read_jsonl(args.reviews)
        key = json.loads(args.key.read_text(encoding="utf-8"))
        report = analyze_experiment(
            trials,
            responses,
            queue,
            key,
            reviews,
            seed=args.seed,
            bootstrap_samples=args.bootstrap_samples,
        )
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print_report(report)
        return 0
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"A/B evaluation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
