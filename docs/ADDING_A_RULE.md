# Adding a New Rule to RuleAudit

This is the practical guide. When you come back to this library in three months and want to audit a new clinical score, follow this. The whole process takes 30 minutes for a simple rule, 2 hours for a complex one.

---

## Quick checklist

1. Locate the original publication. Get the PDF, not a secondary source.
2. Identify the rule's drivers, weights, and category cutoffs from the publication.
3. Create a new file in `ruleaudit/rules/your_rule.py` using the template.
4. Write 10 sanity test cases against published reference patients.
5. Pick or build a realistic input sampler in `ruleaudit/samplers.py`.
6. Create `examples/your_rule/run.py` based on `examples/gap/run.py`.
7. Run it. Read the report. Save the report into `audits/`.

---

## Step 1 — Find the original publication

This is the most important step. **Do not rely on secondary sources** (review articles, Wikipedia, online calculators). I have caught transcription errors in deep-research summaries — they are common.

For each rule you audit, the publication needs to give you:
- The exact driver definitions (what triggers each driver to fire)
- The exact integer weights (how many points each driver contributes)
- The exact category cutoffs (which totals belong to which categories)
- The cohort summary statistics (so you can build a realistic sampler)

If any of these are not in the publication, the audit is structurally incomplete. Mark this in your notes — you can still run the audit, but flag it as "unverified scoring."

---

## Step 2 — Identify the rule's structure

Three questions to answer before coding:

**Q1: How many drivers does this rule have, and are they binary?**

GAP has 5 drivers (RPV, RLL, LDI, RSA, Age). Lewinnek has 4 (after decomposition). SHIVA has 11. All binary. If your rule has a continuous-valued component (e.g., "subtract 1 point per year over 60"), see §"Continuous drivers" below.

**Q2: Are the weights integers?**

Almost all expert-derived rules use small integer weights (0–4 typically). If yours doesn't, the protocol still applies but you'll need to think about Test V (identifiability) more carefully — non-integer weights mean any two distinct firing patterns yield distinct totals, and Test V always passes trivially. Skip Test V for non-integer-weight rules.

**Q3: What are the inputs?**

The inputs are the *raw measurements* the clinician collects, not the drivers. GAP takes 6 inputs (PI, SS, LL1, LL4, GT, age) and computes 5 drivers from them. Lewinnek takes 2 inputs (inclination, anteversion) and decomposes into 4 drivers. Get the input list right; the sampler will sample these.

---

## Step 3 — Create the rule file

Copy `ruleaudit/rules/_template.py` to `ruleaudit/rules/your_rule.py`. Edit:

```python
from dataclasses import dataclass
from typing import Dict

# Your rule's bound constants here
SOME_THRESHOLD = 40.0

@dataclass
class YourRuleCase:
    input_a: float = 0.0
    input_b: float = 0.0
    # ... add all inputs with sensible defaults

def your_rule(inp: Dict) -> Dict:
    """Your rule as a ruleaudit-compatible callable.

    Citation: Author Year, Journal Vol:Pages, DOI.
    """
    a = inp["input_a"]
    b = inp["input_b"]

    drivers = {
        "driver_1": 1 if a > SOME_THRESHOLD else 0,
        "driver_2": 1 if b < -10 else 0,
        # ... one driver per binary indicator
    }
    # Weights are typically encoded as separate dict
    weights = {"driver_1": 2, "driver_2": 3}
    total = sum(weights[k] * v for k, v in drivers.items())

    if total <= 2:    category = "LOW"
    elif total <= 6:  category = "MID"
    else:             category = "HIGH"

    return {"drivers": drivers, "total": total, "category": category}
```

That's the whole file. About 30 lines for a typical rule.

---

## Step 4 — Sanity tests

Before running any audit, prove your implementation matches the publication on 5–10 reference cases.

```python
if __name__ == "__main__":
    cases = [
        # (input_dict, expected_total, expected_category, "publication reference")
        ({"input_a": 30, "input_b": 0}, 0, "LOW", "Fig 6 example A"),
        ({"input_a": 50, "input_b": -15}, 5, "MID", "Fig 6 example B"),
        # ... 5-10 cases drawn from the publication
    ]
    for inp, t_exp, c_exp, ref in cases:
        r = your_rule(inp)
        ok = "✓" if r["total"] == t_exp and r["category"] == c_exp else "✗"
        print(f"  {ok} {inp} → {r['total']} {r['category']} (expected {t_exp} {c_exp}) — {ref}")
```

If any case fails, you have a bug. Find it before continuing — the audit will be invalid otherwise.

This step is non-negotiable. The GAP LDI bug in v0.1 was caught by reading the Yilgor 2017 PDF directly and finding the transcription was wrong. Sanity tests against the publication catch this kind of error immediately.

---

## Step 5 — Build or pick a sampler

Look at `ruleaudit/samplers.py`. Three samplers are provided:

- `asd_realistic()`: ASD-population spinopelvic distribution (PI, SS, LL, GT, age)
- `tha_realistic()`: THA cup placement distribution (inclination, anteversion)
- `uniform_spec(bounds)`: independent uniforms over user-specified bounds

If your rule's inputs match one of these, reuse it. If not, build a new sampler. The pattern:

```python
def your_population_sampler(n: int, seed: int = 42) -> pd.DataFrame:
    """Generate n realistic cases for [your population].

    Distribution parameters are calibrated from [publication, table X].
    """
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "input_a": np.clip(rng.normal(50, 10, n), 20, 80),
        "input_b": rng.normal(15, 8, n),
        # ...
    })
    return df
```

**Sampler quality matters.** A uniform sampler over absurdly wide bounds will make every rule look bad (drivers fire too often or too rarely). A sampler matched to the rule's derivation cohort produces audit findings that are actually about the rule, not about the sampler.

---

## Step 6 — Create the example runner

Copy `examples/gap/run.py` to `examples/your_rule/run.py`. Edit three lines: the rule import, the sampler call, and the output directory.

```python
from ruleaudit import RuleAudit
from ruleaudit.rules.your_rule import your_rule
from ruleaudit.samplers import your_population_sampler

input_spec = {
    "input_a": {"low": 20, "high": 80},
    "input_b": {"low": -20, "high": 40},
}

audit = RuleAudit(rule=your_rule, input_spec=input_spec,
                  sampler=your_population_sampler)
result = audit.run(n_random=10_000, n_saltelli=1024)

from ruleaudit.reporting import render_report
render_report(result, output_dir="examples/your_rule/out/")
print(f"Flags raised: {len(result.flags)}")
```

---

## Step 7 — Read the report

`render_report()` writes:
- `report.md`: the human-readable summary with all flags
- `firing.csv`, `pearson.csv`, `vif.csv`, `sobol.csv`, `identifiability.csv`, `oat.csv`: the raw numbers
- `fig_correlation.png`, `fig_vif.png`, `fig_sobol.png`, `fig_identifiability.png`, `fig_oat.png`: the diagnostic plots

Read the report. Each flag has a structural interpretation (see `INTERPRETING_REPORTS.md`).

After reading, save a permanent copy of the report into `audits/YYYY-MM-DD_your_rule.md` so the audit accumulates over time as part of your living library.

---

## Continuous drivers

Some rules have drivers that are not pure binary indicators — for example, "1 point per decade over 50" or "subtract 0.5 points per cm under the threshold." For RuleAudit, treat these by discretising:

```python
# Continuous driver: 1 point per decade over 50, capped at 3
age_points = min(3, max(0, (age - 50) // 10))
drivers["age_decade_1"] = 1 if age_points >= 1 else 0
drivers["age_decade_2"] = 1 if age_points >= 2 else 0
drivers["age_decade_3"] = 1 if age_points >= 3 else 0
```

This makes the continuous component into a stack of binary indicators that compose additively. Test V (identifiability) becomes meaningful again.

---

## Non-additive rules

If the rule has multiplicative interactions ("score = age × pelvic_tilt" or "if A and B and C") rather than sums, RuleAudit's Test V cannot be applied directly. You have two options:

1. **Decompose the rule into a sum of binary indicators.** This is what we did with Lewinnek (the original is a 2D bounding box; we decomposed into 4 boundary-violation drivers that sum to the violation count).

2. **Apply only Tests I–IV.** Skip Test V, optionally skip Test VI. The audit is partial but still informative for orthogonality and sensitivity.

---

## Common errors

**E1: "My driver fires 100% of the time."** Your sampler is bounded above the trigger threshold, or below it for negative triggers. Re-check the input ranges in your sampler.

**E2: "All VIFs are infinite."** Probably you have a driver that is a deterministic function of another driver, or your sampler has zero variance on one input. Check the firing-rate column — if a driver has firing rate 0.000 or 1.000, the column is constant and VIF is undefined.

**E3: "Test V shows 1 pattern per total."** Your weights are not integers, or your drivers are not properly binary. Check the rule definition.

**E4: "Sobol returns negative S_T."** This is a numerical artifact of small Saltelli sample size. Increase `n_saltelli` to 2048 or 4096.

**E5: "Test III flags every driver as VIF=1.0 exactly."** Your sample size is too small or your drivers are perfectly orthogonal (which is unusual but possible for very simple rules like Lewinnek). Increase n_random to 10,000.

---

## When to stop

You're done auditing a rule when:

1. Sanity tests pass against published reference cases.
2. All flags in the report are interpreted (not just listed).
3. You can articulate the rule's structural failure mode in one sentence (e.g., "GAP has mechanism sprawl at the MD/SD boundary" or "Lewinnek has mechanism erasure in its SAFE label").
4. The audit report is saved into `audits/` for future reference.

If you can't articulate the failure mode, either the rule is structurally clean (good — flag it as "passes structural audit") or your interpretation is incomplete (re-read `INTERPRETING_REPORTS.md`).

---

*Revision history: v0.2 (2026-05) — added decomposition examples (Lewinnek), continuous-driver guidance, non-additive rules section. v0.1 — initial release.*
