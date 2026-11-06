import hashlib, os
A = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
expected = "17911f266b81eda17c74bbd518883bbb3310c6721dd16704ca468173d46aade7"
p = os.path.join(A, "data", "who_oulad_raw.csv")
h = hashlib.sha256(open(p, "rb").read()).hexdigest()
print("who_oulad_raw", h)
print("PASS" if h == expected else "FAIL")
raise SystemExit(0 if h == expected else 1)
