"""Independent naive-baseline audit for M2. Writes only under tests/naive_baselines/."""
import os, json, hashlib
import numpy as np
import pandas as pd

ROOT = os.environ.get("CAPACITY_ROOT")
if not ROOT:
    raise SystemExit("Set CAPACITY_ROOT to the repository root before running this audit.")
OUT = os.path.join(ROOT, "tests", "naive_baselines")
os.makedirs(OUT, exist_ok=True)
RHOS_O = [0.005,0.0075,0.01,0.015,0.02,0.025,0.03,0.04,0.05,0.075,0.10,0.15,0.20,0.30,0.50,1.0]
RHOS_X = [0.005,0.0075,0.01,0.015,0.02,0.025,0.03,0.04,0.05,0.075,0.10,0.15,0.20,0.25,0.30,0.32,0.35,0.40,0.45,0.50,1.0]
DRAWS = 10

def seed_of(key, tag):
    return int(hashlib.sha256(f"{key}|{tag}".encode()).hexdigest()[:8], 16)

def mid_interp(x, y, f=0.9):
    thr = f*y.max(); i = int(np.argmax(y)); lo = x[0]
    for j in range(i,0,-1):
        if y[j-1] < thr <= y[j]:
            lo = x[j-1] + (thr-y[j-1])*(x[j]-x[j-1])/(y[j]-y[j-1]); break
    hi = x[-1]
    for j in range(i,len(y)-1):
        if y[j] >= thr > y[j+1]:
            hi = x[j] + (y[j]-thr)*(x[j+1]-x[j])/(y[j]-y[j+1]); break
    return float(np.sqrt(lo*hi)), float(lo), float(hi)

# ---------------- OULAD ----------------
print("[load] OULAD", flush=True)
S = pd.read_csv(os.path.join(ROOT,"05_SIGNAL","data","oulad_scores.csv"))
E = pd.read_csv(os.path.join(ROOT,"01_DATA","data","oulad_events.csv"),
                usecols=["code_module","code_presentation","id_student","dated"])
S = S.merge(E, on=["code_module","code_presentation","id_student"], how="left", validate="many_to_one")
use = ["code_module","code_presentation","id_student","id_site","date","sum_click"]
V = pd.read_csv(os.path.join(ROOT,"datasets","01_OULAD","studentVle.csv"), usecols=use)
V["week"] = np.floor(V.date.to_numpy()/7).astype(np.int16) + 1
A = (V.groupby(["code_module","code_presentation","id_student","week"], observed=True)
       .sum_click.sum().reset_index())
S = S.merge(A, on=["code_module","code_presentation","id_student","week"], how="left")
S["clicks"] = S.sum_click.fillna(0).astype(float)
S = S.sort_values(["code_module","code_presentation","id_student","week"]).reset_index(drop=True)
g = S.groupby(["code_module","code_presentation","id_student"], observed=True)
S["cum_clicks"] = g.clicks.cumsum()
S["last_active"] = np.where(S.clicks > 0, S.week, np.nan)
S["last_active"] = S.groupby(["code_module","code_presentation","id_student"], observed=True).last_active.ffill()
S["weeks_since"] = np.where(S.last_active.notna(), S.week - S.last_active, S.week + 1)
S["q_model"] = S.q
S["q_activity"] = -S.cum_clicks
S["q_recency"] = S.weeks_since
print("[data] OULAD rows", len(S), "students", S.id_student.nunique(), flush=True)

def run_oulad(qcol, rhos):
    topk, rand, nreach = {}, {}, {}
    for fold, testpres in [("F1","2014B"),("F2","2014J")]:
        sub = S[(S.fold==fold) & (S.code_presentation==testpres)]
        for (mod,pres), gg in sub.groupby(["code_module","code_presentation"], observed=True):
            key = f"{fold}|{mod}|{pres}"
            stud = gg.drop_duplicates("id_student")[["id_student","tau","dated","reachable"]].reset_index(drop=True)
            idx = {s:i for i,s in enumerate(stud.id_student)}
            tau = stud.tau.to_numpy(float); dated = stud.dated.to_numpy()==1; reach = stud.reachable.to_numpy()==1
            n = len(stud); nreach[key] = int(reach.sum())
            Q = np.full((n,26), np.nan); wk = {}
            for k, ss in gg.groupby("week"):
                pos = ss.id_student.map(idx).to_numpy(); Q[pos,int(k)] = ss[qcol].to_numpy(); wk[int(k)] = pos
            for rho in rhos:
                cap = {d: max(1,int(np.ceil(rho*int(((~dated)|(tau>d)).sum())))) for d in range(2,26)}
                for policy in ["topk","random"]:
                    draws = range(DRAWS) if policy=="random" else [0]
                    vals=[]
                    for dr in draws:
                        contacted=np.zeros(n,bool); deliver=np.full(n,-1)
                        rnd=np.random.default_rng(seed_of(key,dr)).permutation(n) if policy=="random" else None
                        for k in range(2,25):
                            cand=wk.get(k)
                            if cand is None: continue
                            cand=cand[~contacted[cand]]
                            if cand.size==0: continue
                            c=cap.get(k+1,0)
                            pick=(cand[np.lexsort((cand,-Q[cand,k]))][:c] if policy=="topk"
                                  else cand[np.argsort(rnd[cand])][:c])
                            deliver[pick]=k+1; contacted[pick]=True
                        caught=reach & (deliver>=0) & (deliver < np.where(dated,tau,np.inf))
                        vals.append(int(caught.sum()))
                    if policy=="topk": topk[(key,rho)]=vals[0]
                    else: rand[(key,rho)]=vals
    # aggregate pooled and per fold
    out={}
    for group, keys in [("F1",[k for k in nreach if k.startswith("F1|")]),
                        ("F2",[k for k in nreach if k.startswith("F2|")]),
                        ("pooled",list(nreach))]:
        nr=sum(nreach[k] for k in keys); y=[]; c5=[]
        for rho in rhos:
            ct=sum(topk[(k,rho)] for k in keys)/nr
            cr=sum(np.mean(rand[(k,rho)]) for k in keys)/nr
            y.append(ct-cr)
        y=np.array(y); peak,lo,hi=mid_interp(np.array(rhos),y)
        i5=int(np.argmin(abs(np.array(rhos)-0.05)))
        out[group]=dict(peak=peak, height=float(y.max()), capture5=float(y[i5]), rho_peak=float(rhos[int(np.argmax(y))]))
    return out

# ---------------- XTX ----------------
print("[load] XTX", flush=True)
X = pd.read_csv(os.path.join(ROOT,"05_SIGNAL","data","xtx_scores_clean.csv"))
Wk = pd.read_csv(os.path.join(ROOT,"05_SIGNAL","data","xtx_weekly_train.csv.gz"))
X = X.merge(Wk, on=["enroll_id","week"], how="left")
X["events"] = X.events.fillna(0).astype(float)
X = X.sort_values(["course_id","enroll_id","week"]).reset_index(drop=True)
gx = X.groupby(["course_id","enroll_id"], observed=True)
X["cum_events"] = gx.events.cumsum()
X["last_active"] = np.where(X.events>0, X.week, np.nan)
X["last_active"] = X.groupby(["course_id","enroll_id"], observed=True).last_active.ffill()
X["weeks_since"] = np.where(X.last_active.notna(), X.week-X.last_active, X.week+1)
X["q_model"]=X.q; X["q_activity"]=-X.cum_events; X["q_recency"]=X.weeks_since
print("[data] XTX rows",len(X),"courses",X.course_id.nunique(),flush=True)

def run_xtx(qcol,rhos):
    topk,rand,nreach={},{},{}
    for cid,gg in X.groupby("course_id",sort=False):
        stud=gg.drop_duplicates("enroll_id")[["enroll_id","tau","event","reachable"]].reset_index(drop=True)
        idx={s:i for i,s in enumerate(stud.enroll_id)}
        tau=stud.tau.to_numpy(float); ev=stud.event.to_numpy()==1; reach=stud.reachable.to_numpy()==1
        n=len(stud); nreach[cid]=int(reach.sum()); W=int(gg.drop_duplicates("enroll_id").W.iloc[0])
        Q=np.full((n,8),np.nan); wk={}
        for k,ss in gg.groupby("week"):
            pos=ss.enroll_id.map(idx).to_numpy(); Q[pos,int(k)]=ss[qcol].to_numpy(); wk[int(k)]=pos
        capd={d:int(((~ev)|(tau>d)).sum()) for d in range(1,W+2)}
        for rho in rhos:
            cap={d:max(1,int(np.ceil(rho*capd.get(d,0)))) for d in range(1,W+2)}
            for policy in ["topk","random"]:
                draws=range(DRAWS) if policy=="random" else [0]
                vals=[]
                for dr in draws:
                    contacted=np.zeros(n,bool); deliver=np.full(n,-1)
                    rnd=np.random.default_rng(seed_of(cid,dr)).permutation(n) if policy=="random" else None
                    for k in range(1,W):
                        cand=wk.get(k)
                        if cand is None: continue
                        cand=cand[~contacted[cand]]
                        if cand.size==0: continue
                        c=cap.get(k+1,0)
                        pick=(cand[np.lexsort((cand,-Q[cand,k]))][:c] if policy=="topk"
                              else cand[np.argsort(rnd[cand])][:c])
                        deliver[pick]=k+1; contacted[pick]=True
                    caught=reach & (deliver>=0) & (deliver < np.where(ev,tau,np.inf))
                    vals.append(int(caught.sum()))
                if policy=="topk": topk[(cid,rho)]=vals[0]
                else: rand[(cid,rho)]=vals
    keys=list(nreach); nr=sum(nreach.values()); y=[]
    for rho in rhos:
        ct=sum(topk[(c,rho)] for c in keys)/nr
        cr=sum(np.mean(rand[(c,rho)]) for c in keys)/nr
        y.append(ct-cr)
    y=np.array(y); peak,lo,hi=mid_interp(np.array(rhos),y)
    i5=int(np.argmin(abs(np.array(rhos)-0.05)))
    return dict(peak=peak,height=float(y.max()),capture5=float(y[i5]),rho_peak=float(rhos[int(np.argmax(y))]))

rows=[]
for qcol in ["q_model","q_activity","q_recency"]:
    print("[run] OULAD",qcol,flush=True)
    o=run_oulad(qcol,RHOS_O)
    for group,v in o.items():
        rows.append(dict(platform="OULAD",baseline=qcol,group=group,**v))
    print("[run] XTX",qcol,flush=True)
    x=run_xtx(qcol,RHOS_X)
    rows.append(dict(platform="XuetangX",baseline=qcol,group="pooled",**x))

T=pd.DataFrame(rows)
T.to_csv(os.path.join(OUT,"naive_results.csv"),index=False)
print(T.to_string(index=False),flush=True)
