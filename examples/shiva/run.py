"""
SHIVA SPIN-THA v7.4 wrapped as a ruleaudit-compatible rule.

Reconstructed from audit documentation; see manuscript Section 3.1.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import numpy as np
from ruleaudit import RuleAudit, InputSpec, InputVar, render_report


# Constants (audit-derived)
TILT_AV  = 0.70
TILT_INC = 0.30
DELTA_SS_STIFF_MAX = 10.0
DELTA_SS_HYPER_MIN = 30.0
PI_LL_MISMATCH     = 10.0
COMB_VERS_LO, COMB_VERS_HI = 35.0, 65.0
FV_UNCERT          = 0.75
WEIGHTS = {
    "delta_ss_stiff":  20, "delta_ss_hyper":  18,
    "pi_ll_mismatch":  15, "comb_vers_oob":   14,
    "low_sit_av_stiff": 16, "low_sit_av_hyper": 8,
    "high_sit_av_stiff": 6,
    "mob_stiff":       10, "mob_hyper":       8,
    "deep_flex":        4, "sit_to_stand":     4,
    "uncert_fv":       12, "uncert_overall":   6,
}


def shiva_rule(inp):
    pi  = inp["pi"]; ll = inp["ll"]
    ss_s = inp["ss_standing"]; ss_t = inp["ss_sitting"]
    pt   = inp["pt_standing"]
    av_p = inp["cup_anteversion"]; inc_p = inp["cup_inclination"]
    fv   = inp.get("femoral_version", 15.0)
    c_fv = inp["conf_fv"]; c_ov = inp["conf_overall"]

    d_ss   = ss_s - ss_t
    pi_ll  = pi - ll
    mob    = "stiff" if d_ss < DELTA_SS_STIFF_MAX else ("hyper" if d_ss > DELTA_SS_HYPER_MIN else "adapt")
    f_av_sit = av_p + TILT_AV * d_ss

    d = {k: 0 for k in WEIGHTS}
    if mob == "stiff": d["delta_ss_stiff"] = WEIGHTS["delta_ss_stiff"]; d["mob_stiff"] = WEIGHTS["mob_stiff"]
    if mob == "hyper": d["delta_ss_hyper"] = WEIGHTS["delta_ss_hyper"]; d["mob_hyper"] = WEIGHTS["mob_hyper"]
    if abs(pi_ll) > PI_LL_MISMATCH:        d["pi_ll_mismatch"]   = WEIGHTS["pi_ll_mismatch"]
    if fv is not None:
        comb = av_p + fv
        if comb < COMB_VERS_LO or comb > COMB_VERS_HI:
            d["comb_vers_oob"] = WEIGHTS["comb_vers_oob"]
    if mob == "stiff" and f_av_sit < 10: d["low_sit_av_stiff"] = WEIGHTS["low_sit_av_stiff"]
    if mob == "hyper" and f_av_sit < 15: d["low_sit_av_hyper"] = WEIGHTS["low_sit_av_hyper"]
    if mob == "stiff" and f_av_sit > 40: d["high_sit_av_stiff"] = WEIGHTS["high_sit_av_stiff"]
    if (d_ss + 7) > 35:                  d["deep_flex"]      = WEIGHTS["deep_flex"]
    if (d_ss / 2) > 20:                  d["sit_to_stand"]   = WEIGHTS["sit_to_stand"]
    if c_fv < FV_UNCERT:                 d["uncert_fv"]      = WEIGHTS["uncert_fv"]
    if c_ov < FV_UNCERT:                 d["uncert_overall"] = WEIGHTS["uncert_overall"]

    total = sum(d.values())
    band = "HIGH" if total >= 60 else ("WATCH" if total >= 30 else "LOW")
    return {"drivers": d, "total": total, "category": band}


def shiva_sampler(rng):
    return {
        "pi":             float(rng.uniform(25, 90)),
        "ll":             float(rng.uniform(10, 80)),
        "ss_standing":    float(rng.uniform(15, 60)),
        "ss_sitting":     float(rng.uniform(-5, 55)),
        "pt_standing":    float(rng.uniform(-10, 40)),
        "cup_anteversion":float(rng.uniform(0, 45)),
        "cup_inclination":float(rng.uniform(25, 60)),
        "femoral_version":float(rng.uniform(-20, 60)),
        "conf_fv":        float(rng.uniform(0.3, 1.0)),
        "conf_overall":   float(rng.uniform(0.3, 1.0)),
    }


spec = InputSpec(
    vars=[
        InputVar("pi", 25, 90), InputVar("ll", 10, 80),
        InputVar("ss_standing", 15, 60), InputVar("ss_sitting", -5, 55),
        InputVar("pt_standing", -10, 40),
        InputVar("cup_anteversion", 0, 45), InputVar("cup_inclination", 25, 60),
        InputVar("femoral_version", -20, 60),
        InputVar("conf_fv", 0.3, 1.0), InputVar("conf_overall", 0.3, 1.0),
    ],
    joint_sampler=shiva_sampler,
)

seeds = {
    "STIFF": dict(pi=58, ll=42, ss_standing=38, ss_sitting=33, pt_standing=20,
                  cup_anteversion=18, cup_inclination=42, femoral_version=12,
                  conf_fv=0.7, conf_overall=0.8),
    "ADAPT": dict(pi=55, ll=50, ss_standing=38, ss_sitting=18, pt_standing=18,
                  cup_anteversion=20, cup_inclination=40, femoral_version=15,
                  conf_fv=0.9, conf_overall=0.9),
    "HYPER": dict(pi=52, ll=58, ss_standing=42, ss_sitting=8, pt_standing=14,
                  cup_anteversion=22, cup_inclination=38, femoral_version=20,
                  conf_fv=0.85, conf_overall=0.85),
}

audit = RuleAudit(rule=shiva_rule, input_spec=spec)

if __name__ == "__main__":
    print("Running SHIVA SPIN-THA audit...")
    result = audit.run(n_random=10000, seeds=seeds, n_saltelli=512)
    out = pathlib.Path(__file__).parent / "out"
    rpath = render_report(result, out, title="SHIVA SPIN-THA v7.4 — RuleAudit Report")
    n_flags = sum(len(getattr(result, t).flags) for t in ["firing", "correlation", "vif", "sensitivity", "identifiability"])
    print(f"Wrote report → {rpath}")
    print(f"Flags raised: {n_flags}")
