---
name: recursive-capability-architect
description: "Evidence-governed architect for turning a complex recurring operation into three accountable loops: a stable Producer, an independent Verifier, and an outcome-driven Improver. Use when the user asks to build a self-improving business capability, recursive operating system, incumbent/challenger program, public/private evaluation split, fixed-budget experiment, held-out validation, human-gated promotion, or a governed path from real outcomes back into SOP and Skills. Trigger for 递归能力系统、三环系统、生产验真进化、复杂业务能力架构、稳定生产者、独立验证者、结果驱动改进、隐藏评估、挑战版本、能力晋级、真实结果回流. Do not use for one-off execution, a retrospective alone, a single artifact review, or merely scaffolding a Skill file."
metadata:
  version: "0.1.0-experimental"
  maturity: "experimental"
---

# Recursive Capability Architect

## Role

Turn a recurring, high-complexity operation into an evidence-governed learning system:

`stable Producer -> independent Verifier -> outcome-driven Improver -> governed promotion`

This skill designs the operating architecture. It does not perform the domain work, grade its own output, or promote a rule because one case succeeded.

## Boundary And Routing

| Need | Route |
|---|---|
| Execute one domain task | The relevant domain Skill |
| Reconstruct lessons from project history | `$super-project-skill-distiller` |
| Train or scaffold one concrete Skill | `$skill-trainer-recursive` and `$skill-creator` |
| Verify one claimed result | `$evidence-gate` or the domain completion reviewer |
| Govern a project registry or dashboard | The relevant lifecycle/strategy governor |
| Design the Producer-Verifier-Improver system | This Skill |

Do not activate the full architecture for a one-off task with no recurring operation or measurable downstream outcome. Route it to the smallest reliable existing capability.

## Required Reading

- Read `references/three_loop_architecture.md` before assigning ownership or visibility.
- Read `references/evaluation_and_promotion.md` before defining experiments or promotion.
- Read `references/feedback_to_capability.md` before converting feedback into a production rule.
- Read `references/methodology_provenance.md` when explaining recursive-improvement claims and their limits.
- Treat the JSON files in `assets/templates/` as public interface examples.

## Workflow

### R0 Outcome Boundary

Define the recurring operation, intended human/business outcome, quality floor, optimization horizon, protected values, prohibited optimizations, and final human veto. Separate:

- `completion_quality`: whether the artifact or service is acceptable;
- `outcome_effectiveness`: whether it caused the desired real-world result;
- `system_learning`: whether a changed rule improves results under comparable conditions.

If no real outcome can be observed yet, set maturity to `baseline_building`. Do not invent a proxy and call it effectiveness.

### R1 Capability Census

Use `$zhiku-market` and local inspection to find the smallest reliable set of Producer, Verifier, evidence, experiment, and governance capabilities. Reuse installed skills before creating new ones. Record responsibility gaps explicitly.

### R2 Producer Contract

Design a stable Producer with:

- inputs, phases, state transitions and artifacts;
- one owner for each decision node;
- completion gates and explicit return paths;
- public quality evidence it may read;
- a frozen incumbent version during a registered trial.

The Producer must not see private outcome weights, survival decisions, or future challenger tuning information.

### R3 Verifier Contract

Create an independent Verifier that binds evidence to the current artifact identity. Separate machine checks, human experience checks and downstream outcome checks. A hard redline, stale artifact, missing normal-speed review, or unverified external write blocks acceptance regardless of weighted score.

### R4 Improver Contract

Design incumbent/challenger experiments with:

- one preregistered primary variable;
- fixed human, tool, sourcing, compute and elapsed-time budgets;
- heterogeneous task families;
- a held-out family or batch;
- parent-outcome dependencies before child challengers begin;
- rejection records for failed proposals.

Do not tune a challenger after reading its private result. Fork a new lineage.

### R5 Visibility And Identity Gate

Build a producer-visible bundle that contains only public contracts, trial manifests and public quality records. Keep private outcomes, weights and selection decisions outside it. Bind every trial to an artifact hash, version, completion receipt, human-review receipt and publication identity when applicable.

Run:

```bash
python3 scripts/recursive_capability.py build-producer-view \
  --root "$SYSTEM_ROOT" \
  --output "$SYSTEM_ROOT/producer-visible"
```

### R6 Result Return

Wait for the registered observation window. Normalize outcomes within an appropriate cohort, record contamination and cost, then issue an eligible, ineligible or insufficient-evidence result. Completion quality and outcome effectiveness remain separate records.

### R7 Governed Promotion

Require conjunctive evidence across multiple cases, batches and task families. Promotion must pass budget, held-out, regression, transfer, hard-redline and human-veto gates. Update only the smallest responsible rule, preserve rollback, and issue a learning receipt. Never edit a production Skill automatically from numeric selection alone.

## Commands

```bash
# Create a generic three-loop system package
python3 scripts/recursive_capability.py init \
  --root "$SYSTEM_ROOT" \
  --system-id example-system \
  --objective "Improve a recurring operation under comparable cost"

# Validate architecture, identity, visibility, dependency and budget rules
python3 scripts/recursive_capability.py validate --root "$SYSTEM_ROOT"

# Evaluate evidence for governed promotion without modifying production
python3 scripts/recursive_capability.py check-promotion \
  --root "$SYSTEM_ROOT" \
  --output "$SYSTEM_ROOT/promotion_receipt.json"

# Run deterministic positive and negative fixtures
python3 scripts/self_test.py
```

## Required Artifacts

- `system_manifest.json`
- `capability_graph.json`
- one `trial_manifest.json` per trial
- one `public_quality_record.json` per completed artifact
- private outcome records stored outside the producer-visible bundle
- `promotion_receipt.json`
- `learning_receipt.json` after any accepted, rejected or deferred change

## Hard Redlines

- Never use completion quality as a proxy for real-world effectiveness.
- Never expose private scores, weights or survival decisions to the Producer.
- Never preregister after publication or choose only successful cases retrospectively.
- Never count budget growth as capability improvement.
- Never let a high score offset a fact, safety, trust, experience or identity redline.
- Never use old screenshots, old manifests or stale hashes to prove the current artifact passed.
- Never promote from a single success, one task family, or a missing held-out test.
- Never let generated prose override the canonical machine-readable state.
- Never claim Level 1 recursive improvement from architecture, delegation or synthetic tests alone.

## Status Language

- `baseline_building`: real comparable outcomes are insufficient.
- `experimental_level_0`: the loops exist; net-positive improvement is unproven.
- `promotion_candidate`: deterministic promotion gates passed; human approval is pending.
- `approved_for_governed_merge`: human approval exists; production merge and regression are still required.
- `production_promoted`: the smallest rule was merged, validated and deployed with rollback evidence.

## Acceptance

The architecture is usable only when:

- local Skill validation and `scripts/self_test.py` pass;
- Producer, Verifier and Improver have non-overlapping decision authority;
- the producer-visible bundle contains no private outcome data;
- artifact identity and observation-window dependencies validate;
- promotion emits a deterministic receipt and never edits production automatically;
- a human can veto facts, safety, brand, trust, experience or irreversible change;
- every change ends with an evidence-backed learning receipt.
