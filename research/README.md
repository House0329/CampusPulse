# Synthetic Evaluation Data

Files in this folder are generated for interface prototyping, chart testing and acceptance-target design.

They do not represent recruited participants or observed human behaviour and must not be reported as a human-subject study.

## What `synthetic_evaluation.csv` is

- `data_type` is always `synthetic_illustrative`.
- Rows are 12 simulated task profiles × 3 tasks × 2 conditions (`baseline_a` vs `campuspulse_b`).
- Numeric values are drawn from design-target centres in the build spec, with a small seeded jitter (`seed=2026`).
- Conditions: **Baseline A** is a static place list with an overall rating; **CampusPulse B** is the task-first prototype.

## What it is not

- Not a usability test with students.
- Not evidence that CampusPulse reduced decision time or increased confidence in the real world.
- Not something to caption as “n = 12 participants”.

## Regenerating

```bash
python scripts/generate_synthetic_eval.py
```

## Portfolio wording

> Because recruited testing was not feasible within the prototype constraints, I used a synthetic evaluation benchmark to stress-test the interaction flow and define future usability measures. These values are illustrative and are not presented as human-subject findings.
