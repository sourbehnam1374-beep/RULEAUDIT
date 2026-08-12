"""
SHIVA SPIN-THA v7.4 — internal spinopelvic risk score for THA (Sour, 2026).

PRESERVED HERE AS THE MOTIVATING AUDIT FOR THE RULEAUDIT PROTOCOL.

The structural pathologies found here (collinearity, dead rules, inert inputs)
are reported in the SHIVA SPIN-THA SoftwareX submission and motivated the
formal protocol presented in the RuleAudit methods paper. This module
preserves the rule as it stood at the time of the audit, for reproducibility.

The deployed engine is v1.0.0 (post-v7.12 patches); see the SHIVA SPIN-THA
repository for the current production version.

Reconstructed from internal audit documentation. Integer weights placed at
the midpoint of audit-reported envelopes where not specified exactly.
Qualitative findings (collinearity, dead rules) follow from rule shape and
are robust to integer weight choice.
"""

from ..core import InputSpec, InputVar


# Constants from audit documentation
TILT_AV  = 0.70
DELTA_SS_STIFF_MAX = 10.0
DELTA_SS_HYPER_MIN = 30.0
PI_LL_MISMATCH     = 10.0
COMB_VERS_LO, COMB_VERS_HI = 35.0, 65.0
FV_UNCERT          = 0.75
WEIGHTS = {
    "delta_ss_stiff":   20, "delta_ss_hyper":   18,
    "pi_ll_mismatch":   15, "comb_vers_oob":    14,
    "low_sit_av_stiff": 16, "low_sit_av_hyper":  8,
    "high_sit_av_stiff": 6,
    "mob_stiff":        10, "mob_hyper":         8,
    "deep_flex":         4, "sit_to_stand":      4,
    "uncert_fv":        12, "uncert_overall":    6,
}


def rule(inp):
    pi = inp["pi"]; ll = inp["ll"]
    ss_s = inp["ss_standing"]; ss_t = inp["ss_sitting"]
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


spec = InputSpec(
    vars=[
        InputVar("pi", 25, 90), InputVar("ll", 10, 80),
        InputVar("ss_standing", 15, 60), InputVar("ss_sitting", -5, 55),
        InputVar("pt_standing", -10, 40),
        InputVar("cup_anteversion", 0, 45), InputVar("cup_inclination", 25, 60),
        InputVar("femoral_version", -20, 60),
        InputVar("conf_fv", 0.3, 1.0), InputVar("conf_overall", 0.3, 1.0),
    ],
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


metadata = {
    "name": "SHIVA SPIN-THA v7.4 (audit reference)",
    "citation": "Sour B, Gharanizadeh K. SPIN-THA: an open, deterministic, "
                "audit-driven web toolkit for spinopelvic planning support "
                "in total hip arthroplasty. SoftwareX 2026 (submitted).",
    "category": "THA spinopelvic risk score",
    "type": "integer-additive multi-driver risk score",
    "driver_names": list(WEIGHTS.keys()),
    "category_names": ["LOW", "WATCH", "HIGH"],
    "validation_history": (
        "Reconstructed from internal audit documentation. Findings reported "
        "in the SHIVA SPIN-THA submission as the audit-driven remediation "
        "step that motivated the RuleAudit protocol. Production engine is "
        "v1.0.0 with structural fixes applied."
    ),
}
