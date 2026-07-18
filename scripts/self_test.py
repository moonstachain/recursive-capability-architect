#!/usr/bin/env python3
"""Regression tests for recursive-capability-architect."""

from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("recursive_capability.py")
SPEC = importlib.util.spec_from_file_location("recursive_capability", MODULE_PATH)
assert SPEC and SPEC.loader
RCA = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RCA)


def write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def make_root(base: Path, name: str) -> Path:
    root = base / name
    RCA.init_system(root, name, f"Objective for {name}")
    return root


def add_trial(root: Path, index: int, batch: str = "batch-1", held_out: bool = False, budget_actual: float = 10) -> dict:
    trial_id = f"trial-{index}"
    digest = f"{index:064x}"[-64:]
    trial = RCA.template("trial_manifest.json")
    trial.update(
        {
            "trial_id": trial_id,
            "system_id": root.name,
            "batch_id": batch,
            "task_family": "family-b" if held_out else "family-a",
            "held_out": held_out,
            "preregistered_at": "2026-01-01T00:00:00+00:00",
            "published_at": "2026-01-02T00:00:00+00:00",
            "artifact_sha256": digest,
            "human_review": {"status": "passed", "artifact_sha256": digest, "receipt_path": "human.json"},
            "budget": {
                "baseline": {"human_minutes": 60, "tool_cost": 10},
                "actual": {"human_minutes": 60, "tool_cost": budget_actual},
            },
            "status": "verified",
        }
    )
    quality = RCA.template("public_quality_record.json")
    quality.update(
        {
            "trial_id": trial_id,
            "artifact_sha256": digest,
            "current_version_verified": True,
            "completion_status": "passed",
            "human_experience_status": "passed",
        }
    )
    trial_root = root / "trials" / trial_id
    write(trial_root / "trial_manifest.json", trial)
    write(trial_root / "public_quality_record.json", quality)
    return trial


def add_outcome(root: Path, trial: dict, lift: float = 7, eligible: bool = True, budget_ratio: float = 1.0) -> None:
    outcome = RCA.template("private_outcome_record.json")
    outcome.update(
        {
            "trial_id": trial["trial_id"],
            "artifact_sha256": trial["artifact_sha256"],
            "observation_hours": 168,
            "eligible": eligible,
            "ineligible_reasons": [] if eligible else ["fixture_ineligible"],
            "outcome_score": 77,
            "matched_baseline_score": 70,
            "outcome_lift": lift,
            "task_family": trial["task_family"],
            "batch_id": trial["batch_id"],
            "held_out": trial["held_out"],
            "family_delta": lift,
            "budget_ratio": budget_ratio,
        }
    )
    write(root / "private" / "outcomes" / f"{trial['trial_id']}.json", outcome)


def expect_error(errors: list[str], text: str) -> None:
    assert any(text in item for item in errors), f"expected {text!r}, got {errors!r}"


def main() -> int:
    tests = 0
    with tempfile.TemporaryDirectory(prefix="rca-self-test-") as tmp:
        base = Path(tmp)

        root = make_root(base, "positive")
        trial = add_trial(root, 1)
        assert RCA.validate_system(root) == []
        RCA.build_producer_view(root, root / "producer-visible")
        assert not list((root / "producer-visible").rglob("private_outcome_record.json"))
        tests += 1

        leak_root = make_root(base, "leak")
        add_trial(leak_root, 2)
        quality_path = leak_root / "trials" / "trial-2" / "public_quality_record.json"
        quality = RCA.load_json(quality_path)
        quality["private_score"] = 99
        write(quality_path, quality)
        expect_error(RCA.validate_system(leak_root), "private fields leaked")
        tests += 1

        late_root = make_root(base, "late")
        late = add_trial(late_root, 3)
        late["preregistered_at"] = "2026-01-03T00:00:00+00:00"
        write(late_root / "trials" / "trial-3" / "trial_manifest.json", late)
        expect_error(RCA.validate_system(late_root), "preregistration must precede publication")
        tests += 1

        dependency_root = make_root(base, "dependency")
        child = add_trial(dependency_root, 4, batch="batch-2")
        child.update(
            {
                "parent_batch_id": "batch-1",
                "parent_outcome_available_at": "2026-01-10T00:00:00+00:00",
                "parent_selection_at": "2026-01-10T01:00:00+00:00",
                "preregistered_at": "2026-01-09T00:00:00+00:00",
            }
        )
        write(dependency_root / "trials" / "trial-4" / "trial_manifest.json", child)
        expect_error(RCA.validate_system(dependency_root), "child preregistration predates")
        tests += 1

        budget_root = make_root(base, "budget")
        add_trial(budget_root, 5, budget_actual=12)
        expect_error(RCA.validate_system(budget_root), "budget exceeds")
        tests += 1

        stale_root = make_root(base, "stale")
        manifest_path = stale_root / "system_manifest.json"
        manifest = RCA.load_json(manifest_path)
        manifest["derived_views"] = [{"path": "strategy_summary.json"}]
        write(manifest_path, manifest)
        write(stale_root / "strategy_summary.json", {"source_state_revision": 0})
        expect_error(RCA.validate_system(stale_root), "stale derived view")
        tests += 1

        one_root = make_root(base, "single-win")
        one = add_trial(one_root, 6)
        add_outcome(one_root, one)
        assert RCA.check_promotion(one_root)["verdict"] == "insufficient_evidence"
        tests += 1

        promotion_root = make_root(base, "promotion")
        for index in range(10, 16):
            trial = add_trial(promotion_root, index, batch="batch-1" if index < 13 else "batch-2", held_out=index == 15)
            add_outcome(promotion_root, trial)
        receipt = RCA.check_promotion(promotion_root)
        assert receipt["verdict"] == "promotion_candidate", receipt
        assert receipt["production_modified"] is False
        tests += 1

        veto_manifest_path = promotion_root / "system_manifest.json"
        veto_manifest = RCA.load_json(veto_manifest_path)
        veto_manifest["human_promotion_decision"] = "vetoed"
        write(veto_manifest_path, veto_manifest)
        assert RCA.check_promotion(promotion_root)["verdict"] == "rejected"
        tests += 1

        evals = RCA.load_json(RCA.SKILL_ROOT / "assets" / "evals" / "evals.json")
        assert len(evals.get("cases") or []) >= 7
        assert {case["id"] for case in evals["cases"]} >= {
            "content-production-positive",
            "research-transfer-positive",
            "delivery-transfer-positive",
            "one-off-route-negative",
        }
        tests += 1

        for domain, objective in (
            ("content-domain", "Improve recurring content production from real audience outcomes"),
            ("research-domain", "Improve recurring research reports from verified decision adoption"),
            ("delivery-domain", "Improve recurring customer delivery without harming service quality"),
        ):
            domain_root = base / domain
            RCA.init_system(domain_root, domain, objective)
            domain_manifest = RCA.load_json(domain_root / "system_manifest.json")
            assert set(domain_manifest["roles"]) == {"producer", "verifier", "improver", "human_owner"}
            assert set(domain_manifest["visibility"]) == {"producer_visible", "private"}
            assert RCA.validate_system(domain_root) == []
            tests += 1

    print(json.dumps({"status": "passed", "tests": tests}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
