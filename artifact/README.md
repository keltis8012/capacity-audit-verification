# OULAD capacity-audit artifact

This directory closes the provenance gap for the OULAD curves reported in the
manuscript. It is not a reimplementation of the audit; it is the exact producer
used for the submitted curve, plus its frozen outputs.

## Files

- code/01_who_oulad.py: the generator. It reads
  05_SIGNAL/data/oulad_scores.csv and 01_DATA/data/oulad_events.csv from
  CAPACITY_ROOT, and writes the curves plus who_oulad_raw.csv.
- data/who_oulad_raw.csv: frozen raw curve table. SHA-256:
  17911f266b81eda17c74bbd518883bbb3310c6721dd16704ca468173d46aade7.
- data/delta_who_oulad.csv: aggregated Delta(rho) curves.
- MANIFEST.sha256: hashes of the frozen outputs and the generator.
- tests/verify_artifact.py: independent hash check.

## Reproduce

From a checkout that contains 05_SIGNAL/ and 01_DATA/:

    export CAPACITY_ROOT=/path/to/capacity-audit
    export OUTDIR=/tmp/oulad_artifact
    export OUTREP=/tmp/oulad_artifact
    python code/01_who_oulad.py
    sha256sum /tmp/oulad_artifact/who_oulad_raw.csv

Expected hash:
17911f266b81eda17c74bbd518883bbb3310c6721dd16704ca468173d46aade7.

The generator uses fixed seeds and fixed presentation lists; a rerun must
produce the same hash, not merely the same rounded peaks. The artifact check
in tests/verify_artifact.py enforces the byte hash.


## Naive-baseline audit (M2)

- naive/naive_baselines.py: independent cumulative-activity and recency rules,
  run through the same weekly delivery policy as the learned ranking.
- naive/naive_results.csv: model, activity, and recency results for OULAD and
  XuetangX at the 5% budget, with peak positions.
- naive/verify_naive.py: checks the model-arm values against the frozen
  delta_who_oulad.csv and delta_who_xtx_clean.csv, then checks all baseline
  rows are present.
- NAIVE_MANIFEST.sha256: hashes for the three files.

Run with:
    export CAPACITY_ROOT=/path/to/capacity-audit
    python naive/naive_baselines.py
    python naive/verify_naive.py
