"""
Lewinnek safe zone — Lewinnek GE et al., JBJS Am 1978;60:217-220.

Bounding-box rule for THA cup orientation:
    inclination 40° ± 10°  (safe = [30°, 50°])
    anteversion 15° ± 10°  (safe = [5°, 25°])

Decomposed into four boundary-violation drivers for structural audit:
    inc_low  : inclination < 30°
    inc_high : inclination > 50°
    av_low   : anteversion < 5°
    av_high  : anteversion > 25°

Total = number of violated boundaries (0, 1, 2).
Categories: SAFE (0), MIXED (1), UNSAFE (2).
"""

from ..core import InputSpec, InputVar


INC_LO, INC_HI = 30.0, 50.0
AV_LO,  AV_HI  =  5.0, 25.0


def rule(inp):
    inc = inp["cup_inclination"]
    av  = inp["cup_anteversion"]
    drivers = {
        "inc_low":  1 if inc < INC_LO else 0,
        "inc_high": 1 if inc > INC_HI else 0,
        "av_low":   1 if av  < AV_LO  else 0,
        "av_high":  1 if av  > AV_HI  else 0,
    }
    total = sum(drivers.values())
    if total == 0:   category = "SAFE"
    elif total == 1: category = "MIXED"
    else:            category = "UNSAFE"
    return {"drivers": drivers, "total": total, "category": category}


spec = InputSpec(
    vars=[
        InputVar("cup_inclination", 0,  80),
        InputVar("cup_anteversion", -10, 60),
    ],
)


seeds = {
    "center": dict(cup_inclination=40, cup_anteversion=15),
    "low":    dict(cup_inclination=25, cup_anteversion=0),
    "high":   dict(cup_inclination=55, cup_anteversion=30),
}


metadata = {
    "name": "Lewinnek safe zone (1978)",
    "citation": "Lewinnek GE, Lewis JL, Tarr R, Compere CL, Zimmerman JR. "
                "Dislocations after total hip-replacement arthroplasties. "
                "JBJS Am 1978;60:217-220.",
    "category": "THA cup orientation",
    "type": "bounding-box rule (binary classifier)",
    "driver_names": ["inc_low", "inc_high", "av_low", "av_high"],
    "category_names": ["SAFE", "MIXED", "UNSAFE"],
    "validation_history": (
        "Abdel MP et al. CORR 2016;474:386-391: in 9,784 THAs, "
        "58% of dislocations occurred within the Lewinnek safe zone. "
        "Subsequent systematic reviews (Seagrave 2017, multiple others) confirm "
        "near-zero predictive value of the static-radiographic safe zone."
    ),
}
