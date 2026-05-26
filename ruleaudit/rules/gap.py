"""
GAP score — Global Alignment and Proportion (Yilgor C et al., JBJS 2017;99:1661-1672).
DOI: 10.2106/JBJS.16.01594

Five-component point-based score for predicting mechanical complications
after adult spinal deformity surgery. Verified against Yilgor 2017 Fig 6
and Table IV (the actual PDF, not secondary sources).

Components: RPV, RLL, LDI, RSA, Age.
Total range: 0-13.
Categories: P (0-2), MD (3-6), SD (>=7).
"""

import numpy as np
from ..core import InputSpec, InputVar


# ---------- ideal targets (Yilgor 2017, p1666) ----------
def ideal_ss(pi): return 0.59 * pi + 9.0
def ideal_ll(pi): return 0.62 * pi + 29.0
def ideal_gt(pi): return 0.48 * pi - 15.0


# ---------- component scoring (Yilgor 2017 Fig 6 / Table IV) ----------
def score_rpv(rpv):
    """Relative Pelvic Version."""
    if rpv < -15.0:        return 3   # severe retroversion
    if rpv <= -7.1:        return 2   # moderate retroversion
    if rpv <= 5.0:         return 0   # aligned
    return 1                          # anteversion (> 5)

def score_rll(rll):
    """Relative Lumbar Lordosis."""
    if rll < -25.0:        return 3   # severe hypolordosis
    if rll <= -14.1:       return 2   # moderate hypolordosis
    if rll <= 11.0:        return 0   # aligned
    return 3                          # hyperlordosis (> 11)

def score_ldi(ldi):
    """Lordosis Distribution Index = (LL_L4S1 / LL_L1S1) * 100.
    Yilgor 2017 corrected scoring: severe hypo=2, mod hypo=1, aligned=0, hyper=3.
    (Hyperlordotic maldistribution is the worst, not severe hypolordotic.)
    """
    if ldi < 40.0:         return 2   # severe hypolordotic maldistribution
    if ldi <= 49.0:        return 1   # moderate hypolordotic maldistribution
    if ldi <= 80.0:        return 0   # aligned
    return 3                          # hyperlordotic maldistribution (> 80)

def score_rsa(rsa):
    """Relative Spinopelvic Alignment."""
    if rsa > 18.0:         return 3   # severe positive malalignment
    if rsa >= 10.1:        return 1   # moderate positive malalignment
    if rsa >= -7.0:        return 0   # aligned
    return 1                          # negative malalignment (< -7)

def score_age(age):
    return 1 if age >= 60.0 else 0


# ---------- the rule callable ----------
def rule(inp):
    pi  = inp["pi"]
    ss  = inp["ss"]
    ll  = inp["ll_l1s1"]
    ll4 = inp["ll_l4s1"]
    gt  = inp["gt"]
    age = inp["age"]

    rpv = ss - ideal_ss(pi)
    rll = ll - ideal_ll(pi)
    ldi = (ll4 / ll) * 100.0 if ll > 0.1 else 0.0
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


# ---------- input specification ----------
spec = InputSpec(
    vars=[
        InputVar("age",      20,  85),
        InputVar("pi",       25,  90),
        InputVar("ss",        5,  65),
        InputVar("ll_l1s1",   5,  85),
        InputVar("ll_l4s1",   0,  70),
        InputVar("gt",      -15,  60),
    ],
)


seeds = {
    "P":  dict(age=45, pi=50, ss=39, ll_l1s1=60, ll_l4s1=39, gt=8),
    "MD": dict(age=58, pi=55, ss=32, ll_l1s1=50, ll_l4s1=22, gt=5),
    "SD": dict(age=70, pi=60, ss=22, ll_l1s1=35, ll_l4s1=12, gt=25),
}


metadata = {
    "name": "GAP score (Yilgor 2017)",
    "citation": "Yilgor C, Sogunmez N, Boissiere L, et al. Global Alignment and "
                "Proportion (GAP) Score. JBJS 2017;99:1661-1672. doi:10.2106/JBJS.16.01594",
    "category": "spinopelvic / adult spinal deformity",
    "type": "integer-additive point-based score",
    "driver_names": ["rpv", "rll", "ldi", "rsa", "age"],
    "category_names": ["P", "MD", "SD"],
    "validation_history": (
        "External validation inconsistent. Bari 2019 (n=149) AUC=0.50. "
        "Kwan 2021 (n=287) AUC=0.66. NASSJ 2025 meta-analysis (32 studies, "
        "5,700+ patients) AUC range 0.53-0.86."
    ),
}
