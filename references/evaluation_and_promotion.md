# Evaluation And Promotion

## Public And Private Evaluation

Public quality answers: `Was the work acceptably produced?`

Private outcome answers: `Did the accepted work improve the intended result?`

Promotion answers: `Did the changed production rule improve outcomes repeatedly, under comparable cost, without harming protected dimensions?`

Do not collapse these questions into one total score.

## Experiment Contract

Every trial must be registered before exposure to its outcome. Record:

- incumbent and challenger lineage;
- one primary changed variable;
- task family, batch, cohort and held-out status;
- expected mechanism and possible harm;
- artifact identity and current-version completion evidence;
- baseline and actual budget;
- observation window and contamination flags.

Child challenger batches may begin only after the parent outcome window and parent selection are complete. Early operational releases remain incumbent evidence, not recursive-improvement evidence.

## Default Promotion Floor

The generic template uses conservative defaults that domains may tighten:

- at least 6 eligible challenger cases;
- at least 2 independent batches;
- median matched outcome lift of at least 5 points;
- at least two-thirds of matched cases improve;
- no task-family median decline below -10 points;
- at least one held-out family or batch improves;
- actual budget no greater than 110% of baseline;
- all current-artifact completion and human gates pass;
- no hard redline;
- final human approval before production merge.

Passing emits `promotion_candidate`, not an automatic production change.

## Anti-Hacking

Invalidate or isolate evidence when it includes:

- paid amplification in a natural-outcome cohort;
- changed outcome definitions after results are known;
- missing observation window;
- unverifiable publication or artifact identity;
- misleading presentation, trust damage or safety harm;
- extra labor, compute or sourcing beyond the registered ceiling;
- platform or environmental anomalies that destroy comparability;
- selective reporting of only successful cases.

## Outcome Design

Use outcomes that reflect the real objective, not the easiest number to collect. Combine leading and lagging signals where appropriate. Preserve protected dimensions as hard constraints or explicit penalties. When no valid outcome exists, remain in `baseline_building`.

## Rollback

Every promotion candidate must identify:

- the smallest rule to change;
- its owner and affected task families;
- historical, transfer and held-out regressions;
- the prior production version;
- an observation period after merge;
- deterministic rollback conditions.
