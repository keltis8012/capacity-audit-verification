import os, json
import pandas as pd

R = os.environ.get("CAPACITY_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
T = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)),"naive_results.csv"))
O = pd.read_csv(os.path.join(R,"04_PREMIUM","data","delta_who_oulad.csv"))
X = pd.read_csv(os.path.join(R,"04_PREMIUM","data","delta_who_xtx_clean.csv"))
ok=True
def chk(name, got, exp, tol=5e-4):
    global ok
    good=abs(got-exp)<=tol
    print(("PASS " if good else "FAIL ")+name, got, "vs", exp)
    ok=ok and good
# canonical 5% curves
for fold in ["F1","F2"]:
    v=O[(O.fold==fold)&(O.rho==0.05)].d_who.iloc[0]
    got=T[(T.platform=="OULAD")&(T.baseline=="q_model")&(T.group==fold)].capture5.iloc[0]
    chk("OULAD "+fold+" capture5", got, v)
chk("XTX capture5", T[(T.platform=="XuetangX")&(T.baseline=="q_model")].capture5.iloc[0], X[X.rho==0.05].d_who.iloc[0])
# model peaks/heights
chk("OULAD model peak", T[(T.platform=="OULAD")&(T.baseline=="q_model")&(T.group=="pooled")].peak.iloc[0], 0.0385, 1e-4)
chk("OULAD model height", T[(T.platform=="OULAD")&(T.baseline=="q_model")&(T.group=="pooled")].height.iloc[0], 0.156845, 1e-5)
chk("XTX model peak", T[(T.platform=="XuetangX")&(T.baseline=="q_model")].peak.iloc[0], 0.272186, 1e-5)
chk("XTX model height", T[(T.platform=="XuetangX")&(T.baseline=="q_model")].height.iloc[0], 0.061470, 1e-5)
# all baselines present
for b in ["q_activity","q_recency"]:
    for p in ["OULAD","XuetangX"]:
        chk(f"{p} {b} present", float(T[(T.platform==p)&(T.baseline==b)].height.notna().sum()), 3.0 if p=="OULAD" else 1.0, 0)
print("OVERALL", "PASS" if ok else "FAIL")
raise SystemExit(0 if ok else 1)
