#!/usr/bin/env python3
"""Regenerate data_manifest.json after the frozen inputs change."""
import hashlib
import json
import sys
from pathlib import Path

FILES = [
    "01_DATA/data/oulad_events.csv",
    "01_DATA/data/xtx_train_truth.csv",
    "01_DATA/data/xtx_agg_train.csv",
    "01_DATA/data/kdd_events_train.csv",
    "04_PREMIUM/data/delta_who_oulad.csv",
    "04_PREMIUM/data/delta_who_xtx_clean.csv",
    "04_PREMIUM/data/decision_map.csv",
    "04_PREMIUM/reports/full_swap.json",
    "04_PREMIUM/reports/kdd_prediction.json",
    "04_PREMIUM/reports/kdd_observation.json",
    "05_SIGNAL/data/oulad_scores.csv",
    "05_SIGNAL/data/xtx_scores_clean.csv",
    "10_PAPER/figs/fig_manifest.json",
    "build/manuscript.md",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    out = {rel: {"bytes": (root / rel).stat().st_size, "sha256": sha256(root / rel)} for rel in FILES}
    (Path(__file__).parent / "data_manifest.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"wrote {len(out)} entries")


if __name__ == "__main__":
    main()
