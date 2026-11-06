"""OULAD WHO curves.

DO NOT OVERWRITE who_oulad_raw.csv during verification: write to a temp
file and compare values; the raw artefact is hash-anchored (17911f266b81eda1).
"""
"""07_POLICY / Delta_who on OULAD, v3.

Adds (audit 2026-10-31 round 6):
  - fine grid around the peak (0.005..0.30, 14 points)
  - rho_rel = rho * D / pi_R (D = decision weeks, pi_R = reachable share)
  - bootstrap resamples presentations AND the random draw (seed variance)
  - peak-location distribution (band-left / in / right)
"""
import hashlib, json, os
import numpy as np
import pandas as pd

ROOT = os.environ.get("CAPACITY_ROOT")
if not ROOT:
    raise SystemExit("Set CAPACITY_ROOT to the repository root before running this generator.")
SCORES = os.path.join(ROOT, "05_SIGNAL", "data", "oulad_scores.csv")
EVENTS = os.path.join(ROOT, "01_DATA", "data", "oulad_events.csv")
OUTD = os.environ.get("OUTDIR", os.path.join(ROOT, "04_PREMIUM", "data"))
OUTR = os.environ.get("OUTREP", os.path.join(ROOT, "04_PREMIUM", "reports"))
os.makedirs(OUTD, exist_ok=True); os.makedirs(OUTR, exist_ok=True)

RHOS = [0.005, 0.0075, 0.01, 0.015, 0.02, 0.025, 0.03, 0.04, 0.05, 0.075, 0.10, 0.15, 0.20, 0.30, 0.50, 1.0]
DEC = list(range(2, 25)); DRAWS = 10; B = 1000
BAND = (0.01, 0.03)

scores = pd.read_csv(SCORES)
ev = pd.read_csv(EVENTS, usecols=["code_module", "code_presentation", "id_student", "dated"])
scores = scores.merge(ev, on=["code_module", "code_presentation", "id_student"], how="left", validate="many_to_one")
assert scores.dated.notna().all()


def seed_of(key, tag):
    return int(hashlib.sha256(f"{key}|{tag}".encode()).hexdigest()[:8], 16)


def run_pres(g, rho, policy, key, draw=0):
    stud = g.drop_duplicates("id_student")[["id_student", "tau", "dated", "reachable"]].reset_index(drop=True)
    idx = {s: i for i, s in enumerate(stud.id_student)}
    tau = stud.tau.to_numpy(float); dated = stud.dated.to_numpy() == 1
    reach = stud.reachable.to_numpy() == 1
    n = len(stud)
    Q = np.full((n, 26), np.nan); wk = {}
    for k, sub in g.groupby("week"):
        pos = sub.id_student.map(idx).to_numpy(); Q[pos, int(k)] = sub.q.to_numpy(); wk[int(k)] = pos
    cap = {d: max(1, int(np.ceil(rho * int(((~dated) | (tau > d)).sum())))) for d in range(2, 26)}
    contacted = np.zeros(n, bool); deliver = np.full(n, -1)
    rnd = np.random.default_rng(seed_of(key, draw)).permutation(n) if policy == "random" else None
    for k in DEC:
        cand = wk.get(k)
        if cand is None: continue
        cand = cand[~contacted[cand]]
        if cand.size == 0: continue
        c = cap.get(k + 1, 0)
        pick = (cand[np.lexsort((cand, -Q[cand, k]))][:c] if policy == "topk"
                else cand[np.argsort(rnd[cand])][:c])
        deliver[pick] = k + 1; contacted[pick] = True
    caught = reach & (deliver >= 0) & (deliver < np.where(dated, tau, np.inf))
    assert contacted.sum() == int((deliver >= 0).sum())
    return int(caught.sum()), int(reach.sum()), int(contacted.sum())


topk, rand, nstud, nreach = {}, {}, {}, {}
for fold, testpres in [("F1", "2014B"), ("F2", "2014J")]:
    sub = scores[(scores.fold == fold) & (scores.code_presentation == testpres)]
    for (mod, pres), g in sub.groupby(["code_module", "code_presentation"], observed=True):
        key = f"{fold}|{mod}|{pres}"
        nstud[key] = int(g.id_student.nunique())
        for rho in RHOS:
            cc, nn, slots = run_pres(g, rho, "topk", key)
            topk[(key, rho)] = (cc, nn, slots)
            nreach[key] = nn
            vals = []
            for d in range(DRAWS):
                c, _, s = run_pres(g, rho, "random", key, d)
                vals.append((c, s))
            rand[(key, rho)] = vals

keys = {"F1": sorted(k for k in nstud if k.startswith("F1|")),
        "F2": sorted(k for k in nstud if k.startswith("F2|"))}
D = len(DEC)
rows = []
for fold in ["F1", "F2"]:
    pi_R = sum(nreach[k] for k in keys[fold]) / sum(nstud[k] for k in keys[fold])
    for rho in RHOS:
        ct = sum(topk[(k, rho)][0] for k in keys[fold]) / sum(nreach[k] for k in keys[fold])
        cr = sum(np.mean([c for c, s in rand[(k, rho)]]) for k in keys[fold]) / sum(nreach[k] for k in keys[fold])
        rows.append(dict(fold=fold, rho=rho, rho_rel=rho * D / pi_R, C_topk=ct, C_random=cr,
                         d_who=ct - cr, pi_R=pi_R))
T = pd.DataFrame(rows)
print(T.round(4).to_string(index=False))
T.to_csv(os.path.join(OUTD, "delta_who_oulad.csv"), index=False)

raw_rows, draw_rows = [], []
for fold in ["F1", "F2"]:
    for k in keys[fold]:
        for rho in RHOS:
            cc, nn, sl = topk[(k, rho)]
            raw_rows.append(dict(fold=fold, course=k, rho=rho, policy="topk",
                                 caught=cc, n_reach=nn, slots=sl))
            cs = [c for c, s in rand[(k, rho)]]
            ss = [s for c, s in rand[(k, rho)]]
            raw_rows.append(dict(fold=fold, course=k, rho=rho, policy="random",
                                 caught=float(np.mean(cs)), n_reach=nn, slots=float(np.mean(ss))))
            for d, (c, s) in enumerate(rand[(k, rho)]):
                draw_rows.append(dict(fold=fold, course=k, rho=rho, draw=d, caught=c, slots=s))
pd.DataFrame(raw_rows).to_csv(os.path.join(OUTD, "who_oulad_raw.csv"), index=False)
pd.DataFrame(draw_rows).to_csv(os.path.join(OUTD, "who_oulad_random_draws.csv"), index=False)

# bootstrap: resample presentations, and one random draw per course
A = {fold: dict(topk=np.array([[topk[(k, r)][0] for r in RHOS] for k in keys[fold]]),
                rand=np.array([[[rand[(k, r)][d][0] for d in range(DRAWS)] for r in RHOS]
                               for k in keys[fold]]),
                nr=np.array([nreach[k] for k in keys[fold]])) for fold in ["F1", "F2"]}
rng = np.random.default_rng(20261031)
deltas, peaks = {}, {}
for fold in ["F1", "F2"]:
    nC = len(keys[fold]); out = np.zeros((B, len(RHOS)))
    for b in range(B):
        pick = rng.integers(0, nC, nC); draw = rng.integers(0, DRAWS, nC)
        nr = A[fold]["nr"][pick].sum()
        tk = A[fold]["topk"][pick].sum(0)
        rr = A[fold]["rand"][pick, :, draw].sum(0)
        out[b] = tk / nr - rr / nr
    deltas[fold] = out
    mid = []
    for b in range(B):
        v = out[b]; idx = int(np.argmax(v)); best = v[idx]
        ok = np.array(RHOS)[v >= 0.9 * best]
        mid.append(float(np.sqrt(ok.min() * ok.max())))
    peaks[fold] = np.array(mid)

obs_mid = {}
for fold in ["F1", "F2"]:
    v = T[T.fold == fold].d_who.to_numpy(); idx = int(np.argmax(v)); best = v[idx]
    rr = T[T.fold == fold].rho.to_numpy(); ok = rr[v >= 0.9 * best]
    obs_mid[fold] = float(np.sqrt(ok.min() * ok.max()))
    lo = np.quantile(deltas[fold], .025, axis=0); hi = np.quantile(deltas[fold], .975, axis=0)
    T.loc[T.fold == fold, "lo"] = lo; T.loc[T.fold == fold, "hi"] = hi
T.to_csv(os.path.join(OUTD, "delta_who_oulad_ci.csv"), index=False)
print("\n[ci] 95% (presentation + draw resampled)")
print(T[["fold", "rho", "rho_rel", "d_who", "lo", "hi"]].round(4).to_string(index=False))

freq = {}
for fold in ["F1", "F2"]:
    m = peaks[fold]
    freq[fold] = dict(left=float((m < BAND[0]).mean()), in_band=float(((m >= BAND[0]) & (m <= BAND[1])).mean()),
                      right=float((m > BAND[1]).mean()),
                      q05=float(np.quantile(m, .05)), q50=float(np.quantile(m, .5)),
                      q95=float(np.quantile(m, .95)), observed=obs_mid[fold])
print("\n[peak] plateau-midpoint distribution:", json.dumps(freq, indent=2))
json.dump(freq, open(os.path.join(OUTR, "peak_location.json"), "w"), indent=2)

print("\n[topology] saturation check (d_who should fall to ~0):")
print(T[T.rho >= 0.15][["fold", "rho", "C_topk", "C_random", "d_who"]].round(4).to_string(index=False))
