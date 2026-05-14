"""
GAP score wrapped as a ruleaudit-compatible rule.

Run:
    python examples/gap/run.py
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))  # to import ruleaudit

import numpy as np
from ruleaudit import RuleAudit, InputSpec, InputVar, render_report


# ------------------------------------------------------------
# Ideal targets (Yilgor 2017)
# ------------------------------------------------------------
def ideal_ss(pi): return 0.59 * pi + 9.0
def ideal_ll(pi): return 0.62 * pi + 29.0
def ideal_gt(pi): return 0.48 * pi - 15.0


# ------------------------------------------------------------
# Component scoring per Yilgor 2017 Table 2
# ------------------------------------------------------------
def score_rpv(x):
    if x < -15: return 3
    if x <= -7.1: return 2
    if x <= 5:    return 0
    return 1

def score_rll(x):
    if x < -25:   return 3
    if x <= -14.1: return 2
    if x <= 11:   return 0
    return 3

def score_ldi(x):
    if x < 40:    return 3
    if x <= 49:   return 2
    if x <= 80:   return 0
    return 1

def score_rsa(x):
    if x > 18:    return 3
    if x >= 10.1: return 1
    if x >= -7:   return 0
    return 1

def score_age(a):
    return 1 if a >= 60 else 0


# ------------------------------------------------------------
# Rule callable: dict in -> dict out
# ------------------------------------------------------------
def gap_rule(inp):
    age = inp["age"]
    pi  = inp["pi"]
    ss  = inp["ss"]
    ll  = inp["ll_l1s1"]
    ll4 = inp["ll_l4s1"]
    gt  = inp["gt"]

    rpv = ss - ideal_ss(pi)
    rll = ll - ideal_ll(pi)
    ldi = (ll4 / ll) * 100 if ll > 0.1 else 0
    rsa = gt - ideal_gt(pi)

    drivers = {
        "rpv": score_rpv(rpv),
        "rll": score_rll(rll),
        "ldi": score_ldi(ldi),
        "rsa": score_rsa(rsa),
        "age": score_age(age),
    }
    total = sum(drivers.values())
    category = "P" if total <= 2 else ("MD" if total <= 6 else "SD")
    return {"drivers": drivers, "total": total, "category": category}


# ------------------------------------------------------------
# ASD-realistic joint sampler (matches the manuscript Experiment 2)
# ------------------------------------------------------------
def asd_sampler(rng):
    age = float(np.clip(rng.normal(60, 12), 18, 88))
    pi  = float(np.clip(rng.normal(52, 10), 25, 90))
    ss  = float(np.clip(0.6 * pi + rng.normal(0, 8), 5, 65))
    ll  = float(np.clip(0.55 * pi + 25 + rng.normal(0, 15), 5, 85))
    frac = float(np.clip(rng.normal(0.6, 0.18), 0.05, 0.95))
    ll4 = float(np.clip(ll * frac, 0, 70))
    gt  = float(np.clip(0.4 * pi - 0.3 * ll + 0.15 * (age - 50) + rng.normal(0, 8),
                        -15, 60))
    return {"age": age, "pi": pi, "ss": ss,
            "ll_l1s1": ll, "ll_l4s1": ll4, "gt": gt}


# ------------------------------------------------------------
# Spec
# ------------------------------------------------------------
spec = InputSpec(
    vars=[
        InputVar("age",      20,  85),
        InputVar("pi",       25,  90),
        InputVar("ss",        5,  65),
        InputVar("ll_l1s1",   5,  85),
        InputVar("ll_l4s1",   0,  70),
        InputVar("gt",      -15,  60),
    ],
    joint_sampler=asd_sampler,
)

seeds = {
    "P":  dict(age=45, pi=50, ss=39, ll_l1s1=60, ll_l4s1=39, gt=8),
    "MD": dict(age=58, pi=55, ss=32, ll_l1s1=50, ll_l4s1=22, gt=5),
    "SD": dict(age=70, pi=60, ss=22, ll_l1s1=35, ll_l4s1=12, gt=25),
}


audit = RuleAudit(rule=gap_rule, input_spec=spec,
                  driver_names=["rpv", "rll", "ldi", "rsa", "age"])


if __name__ == "__main__":
    print("Running GAP audit...")
    result = audit.run(n_random=10000, seeds=seeds, n_saltelli=512)
    out = pathlib.Path(__file__).parent / "out"
    rpath = render_report(result, out, title="GAP Score — RuleAudit Report")
    print(f"Wrote report → {rpath}")
    print(f"Flags raised: {len(result.firing.flags + result.correlation.flags + result.vif.flags + result.sensitivity.flags + result.identifiability.flags)}")
