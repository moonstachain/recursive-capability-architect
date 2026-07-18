# Feedback To Capability

## The Learning Unit

A comment becomes reusable capability only when it has all of these fields:

`trigger -> responsible decision -> action -> observable evidence -> failure condition -> return path -> regression case`

"Remember next time" is not a capability update.

## Evidence Grades

- `E3 direct`: current artifact, actual outcome, current test result, human observation or recorded event.
- `E2 reconstructed`: traceable transcript, log, project document or downstream artifact.
- `E1 inferred`: plausible but not directly verified.
- `E0 missing`: unavailable.

Production promotion should rely on E3 evidence. E2 may motivate a challenger or repair plan. E1 and E0 must remain visible as uncertainty.

## Feedback Conversion

For each material correction record:

1. What the human or outcome exposed.
2. Which prior assumption failed.
3. Whether the issue is local, domain-wide or system-wide.
4. Which node owns prevention.
5. What evidence will prove the new behavior.
6. What negative example must now fail.
7. What transfer case checks overfitting.
8. Whether the change is rejected, observed, challenged or promoted.

## Learning Receipt

The receipt must keep separate:

- source feedback and evidence grade;
- prior rule and proposed rule;
- responsible Skill or module;
- historical regression result;
- unseen transfer result;
- held-out outcome result;
- human decision;
- merge, deployment and rollback status.

Do not rewrite the original user score or historical verdict. Add a later calibration record.

## Governance Discipline

- Change the smallest responsible rule.
- Keep one machine-readable canonical state.
- Render manuals and dashboards from that state where possible.
- Treat a stale derived document as a validation failure, not an alternate truth.
- Keep private evidence out of public Skill packages.
- Record rejected proposals so they are not repeatedly rediscovered.
