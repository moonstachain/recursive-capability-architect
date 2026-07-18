# Three-Loop Architecture

## Contents

1. System model
2. Ownership contract
3. Visibility contract
4. State model
5. Failure routing

## System Model

The architecture separates three kinds of truth:

1. **Production truth**: what process and artifact were produced.
2. **Completion truth**: whether the current artifact met objective and experiential acceptance.
3. **Outcome truth**: whether the accepted artifact caused the intended downstream result under comparable conditions.

The loops share identities and receipts, not unrestricted data.

## Ownership Contract

| Layer | Owns | May read | Must not decide |
|---|---|---|---|
| Producer | planning, execution, delivery candidate | public brief, incumbent rules, public quality feedback | private weights, survival, promotion |
| Verifier | current-artifact acceptance | artifact, public contract, machine and human evidence | business effectiveness, production promotion |
| Improver | proposals, private outcomes, selection evidence | eligible outcomes, cost, redlines, lineage | domain execution, unilateral production merge |
| Human owner | values, irreversible choices, final veto | all evidence needed for the decision | nothing delegated beyond explicit authorization |

One agent may execute multiple roles only when the records and visibility boundaries remain independently testable. Convenience is not evidence of independence.

## Visibility Contract

Producer-visible:

- objective and constraints;
- current incumbent rules;
- preregistered trial hypothesis;
- public quality record;
- de-identified failure classes already approved for reuse.

Private to evaluator/promoter:

- outcome weights and survival threshold;
- raw downstream metrics when they would bias execution;
- challenger ranking and selection decision;
- unpublished held-out cases;
- contaminated or sensitive business signals.

## State Model

Use explicit states:

`baseline_building -> running -> outcome_waiting -> selection_ready -> promotion_candidate -> approved_for_governed_merge -> production_promoted`

Failure states:

- `needs_revision`: the current artifact failed completion or human review.
- `ineligible`: evidence is contaminated, stale, late, over budget or identity-invalid.
- `insufficient_evidence`: the sample or campaign is too small for the claim.
- `rejected`: the proposed rule did not improve the system or violated a protected value.

## Failure Routing

- Producer failure returns to the responsible production node.
- Verifier failure returns to the exact artifact version; scores cannot offset it.
- Outcome ineligibility does not imply the artifact was poor; it means the trial cannot support learning.
- Promotion failure records the rejected mechanism and prevents silent retesting under a new label.
- Governance drift returns to the canonical manifest before any further decision.
