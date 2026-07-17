#!/usr/bin/env python3
"""Deterministic scaffolding and governance checks for three-loop capability systems."""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import re
import shutil
import statistics
import sys
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = SKILL_ROOT / "assets" / "templates"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
PRIVATE_KEYS = {
    "private_outcome",
    "private_outcomes",
    "private_score",
    "private_weights",
    "raw_outcome",
    "survival_decision",
    "selection_decision",
    "private_path",
    "private_evaluator_config",
}
PUBLISHABLE_STATUSES = {
    "candidate_pending_user_watch",
    "verified",
    "published",
    "outcome_waiting",
    "selection_ready",
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def dump_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_time(value: Any, label: str, errors: list[str]) -> dt.datetime | None:
    if value in (None, ""):
        return None
    try:
        parsed = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt.timezone.utc)
        return parsed
    except ValueError:
        errors.append(f"invalid timestamp for {label}: {value}")
        return None


def template(name: str) -> dict[str, Any]:
    return load_json(TEMPLATE_ROOT / name)


def init_system(root: Path, system_id: str, objective: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    for child in ("trials", "private/outcomes", "producer-visible", "receipts"):
        (root / child).mkdir(parents=True, exist_ok=True)

    manifest = template("system_manifest.json")
    manifest["system_id"] = system_id
    manifest["objective"] = objective
    graph = template("capability_graph.json")
    graph["system_id"] = system_id
    learning = template("learning_receipt.json")
    learning["system_id"] = system_id
    learning["learning_id"] = f"{system_id}-initial"

    for path, data in (
        (root / "system_manifest.json", manifest),
        (root / "capability_graph.json", graph),
        (root / "receipts" / "learning_receipt.json", learning),
    ):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite existing file: {path}")
        dump_json(path, data)


def find_trials(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    found: list[tuple[Path, dict[str, Any]]] = []
    for path in sorted((root / "trials").glob("*/trial_manifest.json")):
        found.append((path, load_json(path)))
    return found


def budget_ratios(trial: dict[str, Any]) -> list[float]:
    budget = trial.get("budget") or {}
    baseline = budget.get("baseline") or {}
    actual = budget.get("actual") or {}
    ratios: list[float] = []
    for key, base in baseline.items():
        if not isinstance(base, (int, float)) or base < 0:
            continue
        used = actual.get(key, 0)
        if not isinstance(used, (int, float)) or used < 0:
            ratios.append(float("inf"))
        elif base == 0:
            ratios.append(1.0 if used == 0 else float("inf"))
        else:
            ratios.append(float(used) / float(base))
    return ratios


def private_leaks(value: Any, path: str = "$") -> list[str]:
    leaks: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).lower()
            if normalized in PRIVATE_KEYS or normalized.startswith("private_"):
                leaks.append(f"{path}.{key}")
            leaks.extend(private_leaks(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            leaks.extend(private_leaks(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        lowered = value.lower().replace("\\", "/")
        if "/private/" in lowered or lowered.startswith("private/"):
            leaks.append(path)
    return leaks


def validate_system(root: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = root / "system_manifest.json"
    graph_path = root / "capability_graph.json"
    if not manifest_path.exists():
        return ["missing system_manifest.json"]
    if not graph_path.exists():
        errors.append("missing capability_graph.json")
        return errors

    manifest = load_json(manifest_path)
    graph = load_json(graph_path)
    if manifest.get("schema") != "recursive-capability-system-v1":
        errors.append("unsupported system manifest schema")
    if graph.get("schema") != "recursive-capability-graph-v1":
        errors.append("unsupported capability graph schema")
    if graph.get("system_id") != manifest.get("system_id"):
        errors.append("capability graph system_id does not match manifest")

    roles = manifest.get("roles") or {}
    required_roles = {"producer", "verifier", "improver", "human_owner"}
    missing_roles = sorted(required_roles - set(roles))
    if missing_roles:
        errors.append(f"missing roles: {', '.join(missing_roles)}")
    owners = [roles.get(role, {}).get("owner") for role in ("producer", "verifier", "improver")]
    if any(not owner for owner in owners):
        errors.append("producer, verifier and improver require explicit owners")

    visibility = manifest.get("visibility") or {}
    public = set(visibility.get("producer_visible") or [])
    private = set(visibility.get("private") or [])
    overlap = sorted(public & private)
    if overlap:
        errors.append(f"visibility overlap: {', '.join(overlap)}")

    ceiling = float((manifest.get("budget") or {}).get("ceiling_ratio", 1.1))
    minimum_hours = float((manifest.get("observation") or {}).get("minimum_hours", 168))
    for path, trial in find_trials(root):
        label = trial.get("trial_id") or path.parent.name
        if trial.get("schema") != "recursive-capability-trial-v1":
            errors.append(f"{label}: unsupported trial schema")
        primary = str(trial.get("primary_variable") or "").strip()
        if not primary:
            errors.append(f"{label}: missing primary_variable")
        prereg = parse_time(trial.get("preregistered_at"), f"{label}.preregistered_at", errors)
        published = parse_time(trial.get("published_at"), f"{label}.published_at", errors)
        if prereg and published and prereg >= published:
            errors.append(f"{label}: preregistration must precede publication")

        if trial.get("parent_batch_id"):
            available = parse_time(trial.get("parent_outcome_available_at"), f"{label}.parent_outcome_available_at", errors)
            selected = parse_time(trial.get("parent_selection_at"), f"{label}.parent_selection_at", errors)
            if not prereg or not available or not selected:
                errors.append(f"{label}: child trial lacks parent dependency timestamps")
            elif prereg <= max(available, selected):
                errors.append(f"{label}: child preregistration predates parent outcome or selection")

        status = str(trial.get("status") or "")
        artifact_hash = trial.get("artifact_sha256")
        if status in PUBLISHABLE_STATUSES and not SHA256_RE.fullmatch(str(artifact_hash or "")):
            errors.append(f"{label}: publishable trial lacks a valid artifact_sha256")

        record_path = path.parent / "public_quality_record.json"
        if record_path.exists():
            record = load_json(record_path)
            leaks = private_leaks(record)
            if leaks:
                errors.append(f"{label}: private fields leaked into public quality record: {', '.join(leaks)}")
            if artifact_hash and record.get("artifact_sha256") != artifact_hash:
                errors.append(f"{label}: public quality record is bound to a different artifact")
            if status in PUBLISHABLE_STATUSES and record.get("current_version_verified") is not True:
                errors.append(f"{label}: current artifact is not verified")
        elif status in PUBLISHABLE_STATUSES:
            errors.append(f"{label}: missing public_quality_record.json")

        human = trial.get("human_review") or {}
        if status in {"verified", "published", "outcome_waiting", "selection_ready"}:
            if human.get("status") != "passed" or human.get("artifact_sha256") != artifact_hash:
                errors.append(f"{label}: current artifact lacks a hash-bound passed human review")

        ratios = budget_ratios(trial)
        if ratios and max(ratios) > ceiling + 1e-9:
            errors.append(f"{label}: budget exceeds registered ceiling {ceiling:.3f}")
        if float(trial.get("observation_hours") or 0) < minimum_hours and status in {"selection_ready"}:
            errors.append(f"{label}: observation window is shorter than {minimum_hours:g} hours")

    for view in manifest.get("derived_views") or []:
        view_path = root / str(view.get("path") or "")
        if not view_path.exists():
            errors.append(f"missing derived view: {view_path}")
            continue
        try:
            view_data = load_json(view_path)
        except (ValueError, json.JSONDecodeError):
            errors.append(f"derived view is not a JSON object: {view_path}")
            continue
        if view_data.get("source_state_revision") != manifest.get("state_revision"):
            errors.append(f"stale derived view: {view_path}")

    producer_root = root / "producer-visible"
    if producer_root.exists():
        for path in producer_root.rglob("*.json"):
            leaks = private_leaks(load_json(path))
            if leaks:
                errors.append(f"producer-visible leak in {path}: {', '.join(leaks)}")
    return errors


def public_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(manifest)
    result["visibility"] = {"producer_visible": (manifest.get("visibility") or {}).get("producer_visible", [])}
    result.pop("human_promotion_decision", None)
    return result


def build_producer_view(root: Path, output: Path) -> None:
    errors = validate_system(root)
    if errors:
        raise ValueError("system validation failed:\n- " + "\n- ".join(errors))
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    manifest = public_manifest(load_json(root / "system_manifest.json"))
    graph = load_json(root / "capability_graph.json")
    dump_json(output / "system_manifest.public.json", manifest)
    dump_json(output / "capability_graph.json", graph)
    for trial_path, trial in find_trials(root):
        trial_root = output / "trials" / trial_path.parent.name
        dump_json(trial_root / "trial_manifest.json", trial)
        quality_path = trial_path.parent / "public_quality_record.json"
        if quality_path.exists():
            dump_json(trial_root / "public_quality_record.json", load_json(quality_path))
    leaks: list[str] = []
    for path in output.rglob("*.json"):
        leaks.extend(f"{path}: {item}" for item in private_leaks(load_json(path)))
    if leaks:
        shutil.rmtree(output)
        raise ValueError("producer view contains private data:\n- " + "\n- ".join(leaks))


def check_promotion(root: Path) -> dict[str, Any]:
    manifest = load_json(root / "system_manifest.json")
    policy = manifest.get("promotion_policy") or {}
    ceiling = float((manifest.get("budget") or {}).get("ceiling_ratio", 1.1))
    outcomes: list[dict[str, Any]] = []
    invalid: list[str] = []
    trial_index = {trial.get("trial_id"): trial for _, trial in find_trials(root)}

    for path in sorted((root / "private" / "outcomes").glob("*.json")):
        outcome = load_json(path)
        trial_id = str(outcome.get("trial_id") or path.stem)
        trial = trial_index.get(trial_id)
        reasons = list(outcome.get("ineligible_reasons") or [])
        if not trial:
            reasons.append("missing_trial_manifest")
        elif outcome.get("artifact_sha256") != trial.get("artifact_sha256"):
            reasons.append("artifact_identity_mismatch")
        if outcome.get("contamination"):
            reasons.append("contaminated")
        if outcome.get("hard_redlines"):
            reasons.append("hard_redline")
        if float(outcome.get("observation_hours") or 0) < float((manifest.get("observation") or {}).get("minimum_hours", 168)):
            reasons.append("observation_window_incomplete")
        if float(outcome.get("budget_ratio") or float("inf")) > ceiling + 1e-9:
            reasons.append("budget_exceeded")
        if outcome.get("eligible") is not True:
            reasons.append("not_marked_eligible")
        if reasons:
            invalid.append(trial_id)
        else:
            outcomes.append(outcome)

    eligible_ids = [str(item["trial_id"]) for item in outcomes]
    lifts = [float(item.get("outcome_lift") or 0) for item in outcomes]
    batches = {str(item.get("batch_id")) for item in outcomes}
    family_deltas: dict[str, list[float]] = {}
    for item in outcomes:
        family_deltas.setdefault(str(item.get("task_family")), []).append(float(item.get("family_delta") or 0))
    family_medians = {key: statistics.median(values) for key, values in family_deltas.items()}
    held_out_positive = any(item.get("held_out") is True and float(item.get("outcome_lift") or 0) > 0 for item in outcomes)
    max_budget = max((float(item.get("budget_ratio") or 0) for item in outcomes), default=0.0)
    improved_ratio = sum(1 for value in lifts if value > 0) / len(lifts) if lifts else 0.0
    median_lift = statistics.median(lifts) if lifts else 0.0

    criteria = {
        "minimum_eligible_cases": {"actual": len(outcomes), "required": int(policy.get("minimum_eligible_cases", 6))},
        "minimum_batches": {"actual": len(batches), "required": int(policy.get("minimum_batches", 2))},
        "median_lift": {"actual": median_lift, "required": float(policy.get("minimum_median_lift", 5))},
        "improved_ratio": {"actual": improved_ratio, "required": float(policy.get("minimum_improved_ratio", 2 / 3))},
        "family_floor": {"actual": min(family_medians.values(), default=0.0), "required": float(policy.get("family_floor", -10))},
        "held_out_positive": {"actual": held_out_positive, "required": bool(policy.get("require_held_out_positive", True))},
        "budget_ceiling": {"actual": max_budget, "required": ceiling},
    }
    passed = (
        criteria["minimum_eligible_cases"]["actual"] >= criteria["minimum_eligible_cases"]["required"]
        and criteria["minimum_batches"]["actual"] >= criteria["minimum_batches"]["required"]
        and criteria["median_lift"]["actual"] >= criteria["median_lift"]["required"]
        and criteria["improved_ratio"]["actual"] + 1e-9 >= criteria["improved_ratio"]["required"]
        and criteria["family_floor"]["actual"] >= criteria["family_floor"]["required"]
        and (not criteria["held_out_positive"]["required"] or criteria["held_out_positive"]["actual"])
        and criteria["budget_ceiling"]["actual"] <= criteria["budget_ceiling"]["required"] + 1e-9
    )
    human = str(manifest.get("human_promotion_decision") or "pending")
    if not passed:
        verdict = "insufficient_evidence" if len(outcomes) < criteria["minimum_eligible_cases"]["required"] else "rejected"
    elif human == "vetoed":
        verdict = "rejected"
    elif human == "approved":
        verdict = "approved_for_governed_merge"
    else:
        verdict = "promotion_candidate"
    return {
        "schema": "recursive-capability-promotion-receipt-v1",
        "system_id": manifest.get("system_id"),
        "generated_at": utc_now(),
        "verdict": verdict,
        "criteria": criteria,
        "eligible_trial_ids": eligible_ids,
        "ineligible_trial_ids": sorted(set(invalid)),
        "human_decision": human,
        "smallest_responsible_rule": None,
        "rollback_version": None,
        "production_modified": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init_parser = sub.add_parser("init")
    init_parser.add_argument("--root", required=True)
    init_parser.add_argument("--system-id", required=True)
    init_parser.add_argument("--objective", required=True)
    validate_parser = sub.add_parser("validate")
    validate_parser.add_argument("--root", required=True)
    view_parser = sub.add_parser("build-producer-view")
    view_parser.add_argument("--root", required=True)
    view_parser.add_argument("--output", required=True)
    promotion_parser = sub.add_parser("check-promotion")
    promotion_parser.add_argument("--root", required=True)
    promotion_parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    try:
        root = Path(args.root).expanduser().resolve()
        if args.command == "init":
            init_system(root, args.system_id, args.objective)
            print(json.dumps({"status": "created", "root": str(root)}, ensure_ascii=False))
        elif args.command == "validate":
            errors = validate_system(root)
            print(json.dumps({"status": "passed" if not errors else "failed", "errors": errors}, ensure_ascii=False, indent=2))
            return 0 if not errors else 1
        elif args.command == "build-producer-view":
            output = Path(args.output).expanduser().resolve()
            build_producer_view(root, output)
            print(json.dumps({"status": "created", "output": str(output)}, ensure_ascii=False))
        elif args.command == "check-promotion":
            receipt = check_promotion(root)
            output = Path(args.output).expanduser().resolve()
            dump_json(output, receipt)
            print(json.dumps(receipt, ensure_ascii=False, indent=2))
    except (FileExistsError, FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
