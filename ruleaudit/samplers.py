"""
ruleaudit.samplers — reusable joint distributions for synthetic case generation.

Use these in place of writing one-off `joint_sampler` callables when auditing
a new rule. Sampler signatures: f(rng: np.random.Generator) -> dict[str, float]
"""

import numpy as np


def asd_realistic(rng):
    """Adult-spinal-deformity-realistic distribution. Calibrated from
    published cohort summary statistics (Yilgor 2017; Bari 2019; Schwab).
    
    Returns a dict suitable for the GAP rule.
    """
    age = float(np.clip(rng.normal(60, 12), 18, 88))
    pi  = float(np.clip(rng.normal(52, 10), 25, 90))
    ss  = float(np.clip(0.6 * pi + rng.normal(0, 8), 5, 65))
    ll  = float(np.clip(0.55 * pi + 25 + rng.normal(0, 15), 5, 85))
    frac = float(np.clip(rng.normal(0.6, 0.18), 0.05, 0.95))
    ll4 = float(np.clip(ll * frac, 0, 70))
    gt  = float(np.clip(0.4 * pi - 0.3 * ll + 0.15 * (age - 50)
                        + rng.normal(0, 8), -15, 60))
    return {"age": age, "pi": pi, "ss": ss,
            "ll_l1s1": ll, "ll_l4s1": ll4, "gt": gt}


def tha_realistic(rng):
    """THA-realistic cup-placement distribution. Surgeon attempts to hit
    Lewinnek center (40°/15°) with realistic intra-/inter-surgeon noise
    (SDs from cup-placement literature: 6-8°).
    
    Returns a dict suitable for the Lewinnek rule.
    """
    inc = float(np.clip(rng.normal(42, 8), 0, 80))
    av  = float(np.clip(rng.normal(15, 10), -10, 60))
    return {"cup_inclination": inc, "cup_anteversion": av}


def uniform_spec(rng, spec):
    """Generic uniform sampler over a spec's bounds. Use as fallback when
    no domain-specific joint distribution exists."""
    return {v.name: float(rng.uniform(v.low, v.high)) for v in spec.vars}
