"""
GAP score implementation — Global Alignment and Proportion (Yilgor 2017).

Source spec: section 4 of the prior-art report, cross-verified from
Baum 2021 (J Neurosurg Spine), Noh 2020 (Spine J), and gapcalculator.com.

Inputs (six spinopelvic parameters):
    age           years
    pi            pelvic incidence, degrees
    ss            sacral slope, degrees
    ll_l1s1       L1-S1 lumbar lordosis, degrees
    ll_l4s1       L4-S1 lordosis, degrees
    gt            global tilt, degrees

Derived:
    RPV  = SS  -  ideal_SS,  where ideal_SS  = 0.59 * PI + 9
    RLL  = LL_L1S1 - ideal_LL,  where ideal_LL = 0.62 * PI + 29
    LDI  = (LL_L4S1 / LL_L1S1) * 100
    RSA  = GT - ideal_GT,  where ideal_GT = 0.48 * PI - 15

Total = RPV_pts + RLL_pts + LDI_pts + RSA_pts + Age_pts   [0..13]
Category:  P (0-2)  /  MD (3-6)  /  SD (>=7)
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, Optional


# ============================================================
# Ideal targets
# ============================================================
def ideal_ss(pi: float) -> float:  return 0.59 * pi + 9.0
def ideal_ll(pi: float) -> float:  return 0.62 * pi + 29.0
def ideal_gt(pi: float) -> float:  return 0.48 * pi - 15.0


# ============================================================
# Component scoring — bracket lookups per Yilgor 2017 Table 2
# (verbatim per Baum 2021 transcription)
# ============================================================
def score_rpv(rpv: float) -> int:
    if rpv < -15.0:        return 3
    if rpv <= -7.1:        return 2
    if rpv <= 5.0:         return 0
    return 1  # rpv > 5

def score_rll(rll: float) -> int:
    if rll < -25.0:        return 3
    if rll <= -14.1:       return 2
    if rll <= 11.0:        return 0
    return 3  # rll > 11

def score_ldi(ldi: float) -> int:
    # Yilgor 2017 Fig 6 / Table IV
    if ldi < 40.0:         return 2   # severe hypolordotic maldistribution
    if ldi <= 49.0:        return 1   # moderate hypolordotic maldistribution
    if ldi <= 80.0:        return 0   # aligned
    return 3                          # hyperlordotic maldistribution (>80)

def score_rsa(rsa: float) -> int:
    if rsa > 18.0:         return 3
    if rsa >= 10.1:        return 1
    if rsa >= -7.0:        return 0
    return 1  # rsa < -7

def score_age(age: float) -> int:
    return 1 if age >= 60.0 else 0


# ============================================================
# Input case
# ============================================================
@dataclass
class GAPCase:
    age:      float = 55.0
    pi:       float = 55.0
    ss:       float = 41.0      # close to 0.59*55+9 = 41.45
    ll_l1s1:  float = 63.0      # close to 0.62*55+29 = 63.10
    ll_l4s1:  float = 41.0      # 41/63 = ~65%, mid LDI window
    gt:       float = 11.0      # close to 0.48*55-15 = 11.4

    @property
    def rpv(self) -> float: return self.ss - ideal_ss(self.pi)
    @property
    def rll(self) -> float: return self.ll_l1s1 - ideal_ll(self.pi)
    @property
    def ldi(self) -> float:
        if self.ll_l1s1 == 0: return np.nan
        return (self.ll_l4s1 / self.ll_l1s1) * 100.0
    @property
    def rsa(self) -> float: return self.gt - ideal_gt(self.pi)


# ============================================================
# Engine
# ============================================================
ALL_DRIVER_NAMES = ["rpv", "rll", "ldi", "rsa", "age"]


def evaluate(c: GAPCase) -> Dict:
    drivers = {
        "rpv": score_rpv(c.rpv),
        "rll": score_rll(c.rll),
        "ldi": score_ldi(c.ldi),
        "rsa": score_rsa(c.rsa),
        "age": score_age(c.age),
    }
    total = sum(drivers.values())
    if total <= 2:
        category = "P"
    elif total <= 6:
        category = "MD"
    else:
        category = "SD"
    return {
        "drivers":  drivers,
        "total":    total,
        "category": category,
        "rpv":      c.rpv, "rll": c.rll, "ldi": c.ldi, "rsa": c.rsa,
    }


# ============================================================
# Sanity tests against published reference values
# ============================================================
if __name__ == "__main__":
    # Case A: every relative parameter exactly at ideal, age 40 -> total 0, P
    a = GAPCase(age=40, pi=50, ss=ideal_ss(50), ll_l1s1=ideal_ll(50),
                ll_l4s1=0.65 * ideal_ll(50), gt=ideal_gt(50))
    print("A (ideal, age<60):", evaluate(a))

    # Case B: deeply mis-aligned, elderly -> should be SD
    b = GAPCase(age=70, pi=55, ss=15, ll_l1s1=20, ll_l4s1=4, gt=40)
    print("B (severe disprop):", evaluate(b))

    # Case C: moderate
    c = GAPCase(age=58, pi=60, ss=30, ll_l1s1=45, ll_l4s1=18, gt=8)
    print("C (moderate):", evaluate(c))
