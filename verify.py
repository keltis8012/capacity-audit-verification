#!/usr/bin/env python3
"""Independent verification of the capacity-audit manuscript.

This script deliberately does NOT read 00_ARCH/NUMBERS.yaml or KEY_LEDGER.md.
It recomputes values from score files, event files, curve files, and reports,
then compares them with the values printed in the manuscript.

Usage:
    python verify.py --data-root "D:/Paper/.../new_20261030"

The raw/derived inputs are not shipped with this repository; see README.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score


@dataclass
class Check:
    name: str
    expected: object
    actual: object
    delta: object = None
    status: str = "PASS"
    note: str = ""

    def close(self, tol=0.0):
        try:
            self.delta = float(self.actual) - float(self.expected)
            self.status = "PASS" if abs(self.delta) <= tol else "FAIL"
        except Exception:
            self.status = "PASS" if self.actual == self.expected else "FAIL"
        return self


def check(name, expected, actual, tol=0.0, note=""):
    return Check(name, expected, actual, note=note).close(tol)


def warn(name, expected, actual, note):
    c = Check(name, expected, actual, note=note, status="WARN")
    return c


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv(path: Path, **kw):
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path, **kw)


def edge_midpoint(df, value_col="d_who", rho_col="rho", frac=0.9):
    rho = df[rho_col].to_numpy(float)
    d = df[value_col].to_numpy(float)
    imax = int(np.argmax(d))
    dmax = float(d[imax])
    thr = frac * dmax
    above = np.where(d >= thr)[0]
    lo_i, hi_i = int(above[0]), int(above[-1])

    def interp(i0, i1):
        if i1 == i0:
            return float(rho[i0])
        return float(rho[i0] + (rho[i1] - rho[i0]) * (thr - d[i0]) / (d[i1] - d[i0]))

    lo = interp(max(lo_i - 1, 0), lo_i) if lo_i > 0 else float(rho[lo_i])
    hi = interp(min(hi_i + 1, len(d) - 1), hi_i) if hi_i < len(d) - 1 else float(rho[hi_i])
    return dict(dmax=dmax, argmax=float(rho[imax]), mid=float(math.sqrt(lo * hi)),
                lo=lo, hi=hi, n=len(df))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", required=True)
    ap.add_argument("--out", default=str(Path(__file__).parent / "outputs"))
    args = ap.parse_args()
    R = Path(args.data_root).resolve()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    checks: list[Check] = []

    # ------------------------------------------------------------------ paths
    p_oulad_scores = R / "05_SIGNAL/data/oulad_scores.csv"
    p_xtx_scores = R / "05_SIGNAL/data/xtx_scores_clean.csv"
    p_oulad_events = R / "01_DATA/data/oulad_events.csv"
    p_xtx_truth = R / "01_DATA/data/xtx_train_truth.csv"
    p_xtx_agg = R / "01_DATA/data/xtx_agg_train.csv"
    p_kdd_events = R / "01_DATA/data/kdd_events_train.csv"
    p_oulad_curve = R / "04_PREMIUM/data/delta_who_oulad.csv"
    p_xtx_curve = R / "04_PREMIUM/data/delta_who_xtx_clean.csv"
    p_decision = R / "04_PREMIUM/data/decision_map.csv"
    p_full_swap = R / "04_PREMIUM/reports/full_swap.json"
    p_kdd_pred = R / "04_PREMIUM/reports/kdd_prediction.json"
    p_kdd_obs = R / "04_PREMIUM/reports/kdd_observation.json"
    p_manifest = R / "10_PAPER/figs/fig_manifest.json"
    p_manuscript = R / "build/manuscript.md"

    inputs = [
        p_oulad_scores, p_xtx_scores, p_oulad_events, p_xtx_truth, p_xtx_agg,
        p_kdd_events, p_oulad_curve, p_xtx_curve, p_decision, p_full_swap,
        p_kdd_pred, p_kdd_obs, p_manifest, p_manuscript,
    ]
    missing = [str(p) for p in inputs if not p.exists()]
    if missing:
        raise SystemExit("Missing inputs:\n" + "\n".join(missing))

    # ------------------------------------------------ input integrity manifest
    dm_path = Path(__file__).with_name("data_manifest.json")
    dm = json.loads(dm_path.read_text(encoding="utf-8"))
    for rel, meta in dm.items():
        p = R / rel
        if not p.is_file():
            checks.append(Check(f"manifest {rel}", "exists", "missing", status="FAIL"))
            continue
        checks.append(check(f"manifest sha256 {rel}", meta["sha256"], sha256(p), 0, f"{meta['bytes']} bytes"))

    # ------------------------------------------------------- OULAD (Table 1)
    o = read_csv(p_oulad_scores, usecols=[
        "code_module", "code_presentation", "id_student", "week", "q", "y",
        "tau", "withdrawn", "reachable", "fold",
    ])
    ou = o.drop_duplicates(["code_module", "code_presentation", "id_student"])
    checks += [
        check("OULAD rows (score panel)", 15889, len(ou)),
        check("OULAD withdrawals (panel)", 3264, int(ou.withdrawn.sum())),
        check("OULAD reachable (panel)", 2688, int(ou.reachable.sum())),
        check("OULAD horizon E[tau-1] (panel)", 13.0, float((ou.loc[ou.reachable, "tau"] - 1).mean()), 0.05),
        check("OULAD AUC F1 (weekly rows)", 0.6639, float(roc_auc_score(o[o.fold == "F1"].y, o[o.fold == "F1"].q)), 0.0001),
        check("OULAD AUC F2 (weekly rows)", 0.6815, float(roc_auc_score(o[o.fold == "F2"].y, o[o.fold == "F2"].q)), 0.0001),
    ]
    panel_pres = ou[["code_module", "code_presentation"]].drop_duplicates().shape[0]
    all_pres = read_csv(p_oulad_events, usecols=["code_module", "code_presentation"])
    all_pres = all_pres.drop_duplicates().shape[0]
    checks.append(check("OULAD presentations (panel)", 13, panel_pres))
    checks.append(check("OULAD presentations (full)", 22, all_pres))

    # --------------------------------------------------------- XTX (Table 1)
    x = read_csv(p_xtx_scores, usecols=["enroll_id", "course_id", "q", "y", "tau", "event", "reachable"])
    xu = x.drop_duplicates("enroll_id")
    checks += [
        check("XTX rows (panel enrollments)", 134032, len(xu)),
        check("XTX positives (panel)", 96081, int(xu.event.sum())),
        check("XTX reachable (panel)", 72094, int(xu.reachable.sum())),
        check("XTX horizon E[tau-1] (panel)", 3.1, float((xu.loc[xu.reachable, "tau"] - 1).mean()), 0.05),
        check("XTX AUC (weekly rows)", 0.7032, float(roc_auc_score(x.y, x.q)), 0.0001),
    ]
    per_course = x.groupby("course_id").apply(
        lambda g: roc_auc_score(g.y, g.q) if g.y.nunique() > 1 else np.nan,
        include_groups=False,
    ).dropna()
    checks.append(check("XTX course median AUC", 0.6669, float(per_course.median()), 0.0001))

    truth = read_csv(p_xtx_truth)
    agg = read_csv(p_xtx_agg, usecols=["enroll_id", "course_id"])
    checks += [
        check("XTX enrollments (full)", 157943, len(truth)),
        check("XTX positives (full)", 119817, int(truth.truth.sum())),
        check("XTX courses (full)", 247, int(agg.course_id.nunique())),
    ]
    checks.append(check("XTX courses (panel)", 246, int(xu.course_id.nunique())))

    # --------------------------------------------------------- KDD (Table 1)
    k = read_csv(p_kdd_events, usecols=["enrollment_id", "course_id", "tau", "event", "reachable"])
    checks += [
        check("KDD enrollments", 120542, len(k)),
        check("KDD positives", 95581, int(k.event.sum())),
        check("KDD reachable", 44777, int(k.reachable.sum())),
        check("KDD courses", 39, int(k.course_id.nunique())),
        check("KDD horizon E[tau-1]", 2.7, float((k.loc[k.reachable, "tau"] - 1).mean()), 0.05),
    ]

    # --------------------------------------------------------------- curves
    oc = read_csv(p_oulad_curve)
    xc = read_csv(p_xtx_curve)
    peaks = {}
    for fold in ["F1", "F2"]:
        m = edge_midpoint(oc[oc.fold == fold])
        peaks[fold] = m
        checks += [
            check(f"OULAD {fold} peak height", {"F1": 0.1400, "F2": 0.1691}[fold], m["dmax"], 0.0002),
            check(f"OULAD {fold} peak midpoint", {"F1": 0.0384, "F2": 0.0385}[fold], m["mid"], 0.0002),
        ]
    xm = edge_midpoint(xc)
    peaks["XTX"] = xm
    checks += [
        check("XTX peak height", 0.0615, xm["dmax"], 0.0002),
        check("XTX peak midpoint", 0.2722, xm["mid"], 0.0002),
    ]

    captures = {}
    for name, df in [("F1", oc[oc.fold == "F1"]), ("F2", oc[oc.fold == "F2"]), ("XTX", xc)]:
        captures[name] = (
            float(np.interp(0.05, df.rho, df.C_topk)),
            float(np.interp(0.05, df.rho, df.C_random)),
        )
    checks += [
        check("OULAD F1 capture at 5%", 0.639, captures["F1"][0], 0.001),
        check("OULAD F2 capture at 5%", 0.686, captures["F2"][0], 0.001),
        check("XTX capture at 5%", 0.103, captures["XTX"][0], 0.001),
        check("OULAD F1 random at 5%", 0.524, captures["F1"][1], 0.001),
        check("OULAD F2 random at 5%", 0.549, captures["F2"][1], 0.001),
        check("XTX random at 5%", 0.086, captures["XTX"][1], 0.001),
    ]

    ratios = {}
    for rho in (0.01, 0.05):
        xd = float(np.interp(rho, xc.rho, xc.d_who))
        for fold in ("F1", "F2"):
            g = oc[oc.fold == fold]
            ratios[(rho, fold)] = float(np.interp(rho, g.rho, g.d_who)) / xd
    checks += [
        check("ratio 1% F1", 14.75, ratios[(0.01, "F1")], 0.02),
        check("ratio 1% F2", 17.51, ratios[(0.01, "F2")], 0.02),
        check("ratio 5% F1", 6.66, ratios[(0.05, "F1")], 0.02),
        check("ratio 5% F2", 7.91, ratios[(0.05, "F2")], 0.02),
    ]

    # ---------------------------------------------------------------- swap
    base = float(read_csv(p_decision).query("k == 1.0").rho.iloc[0])
    full = json.loads(p_full_swap.read_text())
    swap = float(full["xtx"]["c_star"])
    observed = xm["mid"]
    input_eff = swap - base
    mech_eff = observed - swap
    checks += [
        check("swap base position", 0.431, base, 0.0005),
        check("swap cell (real x estimator)", 0.200, swap, 0.0005),
        check("observed position", 0.2722, observed, 0.0002),
        check("input effect", -0.231, input_eff, 0.001),
        check("mechanical effect", 0.0722, mech_eff, 0.001),
        check("net gap", -0.1588, observed - base, 0.001),
    ]

    # ------------------------------------------------------------- KDD dry run
    pred = json.loads(p_kdd_pred.read_text())
    obs = json.loads(p_kdd_obs.read_text())
    band_lo, band_hi = pred["band_014"]
    ci_lo, ci_hi = obs["ci90"]
    checks += [
        check("KDD prediction mid", 0.4499, float(pred["mid"]), 0.0002),
        check("KDD band lower", 0.3099, float(band_lo), 0.0002),
        check("KDD band upper", 0.5899, float(band_hi), 0.0002),
        check("KDD observed mid", 0.4114, float(obs["mid"]), 0.0002),
        check("KDD observed lower CI", 0.3076, float(ci_lo), 0.0002),
        check("KDD containment gap", 0.0023, float(band_lo - ci_lo), 0.0002),
    ]

    # ------------------------------------------------------------- fig8 spreads
    pos_spread = abs(peaks["F1"]["mid"] - peaks["F2"]["mid"]) / np.mean([peaks["F1"]["mid"], peaks["F2"]["mid"]])
    auc_spread = abs(0.6815 - 0.6639) / 0.6639
    height_spread = abs(peaks["F1"]["dmax"] - peaks["F2"]["dmax"]) / peaks["F1"]["dmax"]
    checks += [
        check("fold position spread", 0.0026, float(pos_spread), 0.0005),
        check("fold AUC spread", 0.0265, float(auc_spread), 0.001),
        check("fold height spread", 0.208, float(height_spread), 0.002),
    ]

    # ------------------------------------------------------------- figure hashes
    manifest = json.loads(p_manifest.read_text())
    fig_dir = p_manifest.parent
    for name, entry in manifest.items():
        if "file" not in entry:
            for field in ("script", "result"):
                rel = entry.get(field)
                if not rel:
                    continue
                p = R / rel
                if p.is_file():
                    checks.append(check(f"{name} {field} sha256", entry.get(f"{field}_sha256"), sha256(p), 0, "byte hash"))
                else:
                    checks.append(Check(f"{name} {field}", "exists", "missing", status="FAIL"))
            continue
        target = fig_dir / entry.get("file", "")
        if not target.is_file():
            checks.append(Check(f"figure {name} file", "exists", "missing", status="FAIL"))
            continue
        checks.append(check(f"figure {name} sha256", entry["sha256"], sha256(target), 0, "byte hash"))
        for rel, expected in (entry.get("data_sha256") or {}).items():
            p = R / rel
            if p.is_file():
                checks.append(check(f"figure {name} data {rel}", expected, sha256(p), 0, "byte hash"))
            else:
                checks.append(Check(f"figure {name} data {rel}", "exists", "missing", status="FAIL"))

    # ---------------------------------------------------------------- text claims
    text = p_manuscript.read_text(encoding="utf-8")
    text_claims = {
        "Table 1 OULAD panel": "15,889",
        "Table 1 XTX panel": "134,032",
        "Table 1 KDD": "120,542",
        "Table 1 OULAD positives": "3,264",
        "Table 1 OULAD reachable": "2,688",
        "Table 1 XTX positives": "96,081",
        "Table 1 XTX reachable": "72,094",
        "Table 1 KDD reachable": "44,777",
        "OULAD peak": "0.0385",
        "XTX peak": "0.2722",
        "dry-run gap": "0.0023",
    }
    for name, token in text_claims.items():
        checks.append(check(f"text contains {name}", True, token in text, 0, f"token {token!r}"))

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "data_root": str(R),
        "n_checks": len(checks),
        "n_pass": sum(c.status == "PASS" for c in checks),
        "n_warn": sum(c.status == "WARN" for c in checks),
        "n_fail": sum(c.status == "FAIL" for c in checks),
        "checks": [asdict(c) for c in checks],
        "peaks": peaks,
        "captures": captures,
        "ratios": {f"{k[0]:.2f}_{k[1]}": v for k, v in ratios.items()},
        "swap": {"base": base, "swap": swap, "observed": observed,
                 "input_effect": input_eff, "mechanical_effect": mech_eff},
    }
    (out / "verification_report.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = ["# Independent verification report", "",
             f"- checks: {payload['n_checks']}",
             f"- pass: {payload['n_pass']}",
             f"- warn: {payload['n_warn']}",
             f"- fail: {payload['n_fail']}", "",
             "| check | expected | actual | status | note |", "|---|---:|---:|---|---|"]
    for c in checks:
        lines.append(f"| {c.name} | {c.expected} | {c.actual} | {c.status} | {c.note} |")
    (out / "verification_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"PASS {payload['n_pass']}  WARN {payload['n_warn']}  FAIL {payload['n_fail']}")
    print(f"report: {out / 'verification_report.json'}")
    if payload["n_fail"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
