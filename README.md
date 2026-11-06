# Capacity-audit manuscript: independent verification

This repository contains the code used to independently re-check the numbers in
the manuscript **“How Many Calls Is a Ranking Worth? Capacity-Constrained
Evaluation of Dropout Prediction.”**

The verification is deliberately independent of the paper's internal registry:
it does **not** read `00_ARCH/NUMBERS.yaml` or `00_ARCH/KEY_LEDGER.md`.
Instead it recomputes values from score files, event files, curve files, and
frozen reports, then checks them against the values printed in
`build/manuscript.md`.

## What is verified

1. **Table 1 cohort accounting**
   - OULAD: 32,593 enrollments, 15,889 test-presentation panel, 3,264 panel
     withdrawals, 2,688 reachable, 13.0-week horizon, 22 full / 13 panel
     presentations.
   - XuetangX: 157,943 enrollments, 134,032 panel, 96,081 positives, 72,094
     reachable, 3.1-week horizon, 247 full / 246 panel courses.
   - KDD: 120,542 enrollments, 95,581 positives, 44,777 reachable, 2.7-week
     horizon, 39 courses.
2. **Discrimination**
   - OULAD AUC 0.6639 (F1) and 0.6815 (F2), recomputed from
     `oulad_scores.csv` (`q` vs `y`).
   - XuetangX pooled AUC 0.7032 and course median 0.6669, recomputed from
     `xtx_scores_clean.csv`.
3. **Peaks and capture**
   - 0.9-plateau midpoint, peak height, and capture at a 5% weekly rate,
     recomputed from the OULAD and XuetangX curve files.
   - OULAD peaks 0.0384 / 0.0385, heights 0.1400 / 0.1691.
   - XuetangX peak 0.2722, height 0.0615.
4. **Operational ratios**
   - 14.75 / 17.51 at 1% and 6.66 / 7.91 at 5%, recomputed from the curves.
5. **Swap decomposition**
   - Base 0.431 from `decision_map.csv`; swap 0.200 from
     `full_swap.json`; observed 0.2722 from the XuetangX curve.
   - Input effect -0.231, mechanical effect +0.0722, net -0.1588.
6. **KDD dry run**
   - Predicted mid 0.4499, band [0.3099, 0.5899], observed mid 0.4114,
     observed 90% interval [0.3076, 0.4448], containment gap 0.0023.
7. **Figure integrity**
   - SHA256 of every figure in `10_PAPER/figs/fig_manifest.json`.
   - SHA256 of the data files listed under that manifest.
8. **Manuscript claims**
   - Presence of the key Table 1 / peak / dry-run values in
     `build/manuscript.md`.

## What is not verified

- **KDD AUC 0.7316** is read from the frozen prediction report
  (`04_PREMIUM/reports/kdd_prediction.json`); the raw KDD score file is not
  part of this repository. The AUC is therefore a report-level check, not a
  raw-score recomputation.
- **Raw KDD logs / OULAD VLE logs** are not redistributed. The repository
  starts from the frozen event/score tables.
- **Figure pixels** are not re-rendered. The figure hashes and the underlying
  numerical files are checked; visual regeneration is outside this script.

## Data layout

The script expects the project root containing:

```
01_DATA/data/oulad_events.csv
01_DATA/data/xtx_train_truth.csv
01_DATA/data/xtx_agg_train.csv
01_DATA/data/kdd_events_train.csv
04_PREMIUM/data/delta_who_oulad.csv
04_PREMIUM/data/delta_who_xtx_clean.csv
04_PREMIUM/data/decision_map.csv
04_PREMIUM/reports/full_swap.json
04_PREMIUM/reports/kdd_prediction.json
04_PREMIUM/reports/kdd_observation.json
05_SIGNAL/data/oulad_scores.csv
05_SIGNAL/data/xtx_scores_clean.csv
10_PAPER/figs/fig_manifest.json
build/manuscript.md
```

The hashes and sizes of these inputs are in `data_manifest.json`; the script verifies them before recomputation.

## Run

```bash
python -m pip install -r requirements.txt
python verify.py --data-root /path/to/new_20261030
```

Outputs:

- `outputs/verification_report.json`
- `outputs/verification_report.md`

A run exits with code 1 if any check fails.

## Result

The committed run reports **92 checks, 92 PASS, 0 WARN, 0 FAIL**.

## Notes on two accounting choices

- The OULAD panel (15,889) is the union of the two **test** presentations
  (13 of 22); it is not all 32,593 enrollments. Table 1 states this in its
  note.
- XuetangX has 247 courses in the full extraction and 246 in the analysis
  panel; Table 1 now reports both columns.

## License

Code: MIT. Data are governed by the original dataset terms (OULAD, XuetangX,
KDD Cup 2015).
