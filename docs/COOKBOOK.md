# RuleAudit Cookbook

Common workflows you'll do repeatedly. Recipes, not tutorials.

---

## Recipe 1 — Audit a published rule end-to-end

Time: 30 minutes for a simple rule.

```python
from ruleaudit import RuleAudit
from ruleaudit.rules.gap import gap_rule
from ruleaudit.samplers import asd_realistic
from ruleaudit.reporting import render_report

audit  = RuleAudit(rule=gap_rule, input_spec={...}, sampler=asd_realistic)
result = audit.run(n_random=10_000, n_saltelli=2048)
render_report(result, output_dir="examples/gap/out/")
```

Look in `examples/gap/out/` for the report.md, CSVs, and figures.

Save the report into the audits archive:

```bash
cp examples/gap/out/report.md audits/$(date +%Y-%m-%d)_gap_v1.md
```

---

## Recipe 2 — Compare two versions of the same rule

When a rule gets updated (e.g., GAP-V, GAP-B, GAPB-Modified), audit both and compare.

```python
from ruleaudit.rules.gap import gap_rule
from ruleaudit.rules.gap_v2 import gap_rule as gap_v2_rule  # hypothetical

r1 = RuleAudit(rule=gap_rule,    sampler=asd_realistic).run(n_random=10_000)
r2 = RuleAudit(rule=gap_v2_rule, sampler=asd_realistic).run(n_random=10_000)

# Compare flags side by side
print(f"v1 flags: {len(r1.flags)} → v2 flags: {len(r2.flags)}")
print(f"v1 patterns at MD/SD boundary: {r1.identifiability_peak()}")
print(f"v2 patterns at MD/SD boundary: {r2.identifiability_peak()}")
```

A new version that *increases* the flag count is going backwards. A new version that addresses a specific flag from v1 is real progress.

---

## Recipe 3 — Audit your own deterministic rule before publishing

If you are building a clinical scoring system, run the audit *before* you publish it. This catches structural pathologies you can fix during development rather than after deployment.

```python
def my_new_rule(inp):
    # your rule logic
    return {"drivers": {...}, "total": ..., "category": ...}

audit  = RuleAudit(rule=my_new_rule, sampler=your_population_sampler)
result = audit.run(n_random=10_000)
render_report(result, output_dir="audits/pre_publish/my_new_rule/")
```

Read the report. Fix what you can. Re-audit. Repeat until you can articulate the rule's structural properties clearly. Then publish — and include the audit report as a supplement.

---

## Recipe 4 — Test sensitivity of audit findings to sampler choice

The sampler is the audit's main free parameter. Verify your findings are robust by re-running the audit with a different (still realistic) sampler.

```python
from ruleaudit.samplers import asd_realistic, uniform_spec

input_spec = {
    "pi":      {"low": 25, "high": 90},
    "ss":      {"low":  5, "high": 65},
    # ...
}

r1 = RuleAudit(rule=gap_rule, sampler=asd_realistic).run(n_random=10_000)
r2 = RuleAudit(rule=gap_rule, sampler=lambda n: uniform_spec(input_spec, n)).run(n_random=10_000)

print(f"ASD-realistic firing rates: {r1.firing_rates()}")
print(f"Uniform-spec firing rates:  {r2.firing_rates()}")
```

If the qualitative findings change drastically between samplers, the audit is sampler-dependent and you should report it carefully. If the qualitative findings hold (collinearity is still there, hidden interactions are still there, mechanism sprawl is still there), the audit is robust.

For GAP and Lewinnek, the qualitative findings hold across ASD-realistic, THA-realistic, and uniform-spec samplers. This is reported in the manuscript.

---

## Recipe 5 — Generate a publication figure from audit results

The figures in the `out/` directory are not publication-ready by default — they have working titles, no captions, no journal-style formatting. To make them publication-ready:

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load the raw data
identifiability = pd.read_csv("examples/gap/out/identifiability.csv")

# Plot to publication standards
fig, ax = plt.subplots(figsize=(5.5, 3.2))
ax.scatter(identifiability["total"], identifiability["n_patterns"],
           s=identifiability["n_cases"] / 50, alpha=0.7, c="#1e3a5f")
ax.axvline(2.5, color="#b8860b", linestyle="--", label="P / MD boundary")
ax.axvline(6.5, color="#a32d20", linestyle="--", label="MD / SD boundary")
ax.set_xlabel("GAP total score")
ax.set_ylabel("Distinct firing patterns")
ax.set_title("Mechanism diversity per GAP total")
ax.legend()
plt.tight_layout()
plt.savefig("manuscript_figure_3.pdf", dpi=300)
```

Save the underlying CSV with the figure so reviewers can reproduce it.

---

## Recipe 6 — Compute MDL calibration debt (Test VI)

This requires a labelled cohort. Most often you won't have one, but when you do:

```python
import pandas as pd
from ruleaudit import RuleAudit

cohort = pd.read_csv("path/to/your/cohort.csv")
# columns: input_1, input_2, ..., outcome_binary

audit  = RuleAudit(rule=gap_rule)
result = audit.run_mdl(cohort, outcome_column="mechanical_complication")
print(f"Expert rule encoding: {result.mdl_expert:.1f} bits")
print(f"L1 baseline encoding: {result.mdl_baseline:.1f} bits")
print(f"Calibration debt:     {result.calibration_debt:.1f} bits")
```

Interpretation:
- debt ≤ 0: expert rule is competitive with the regression
- debt > 0 but small: expert rule pays interpretability cost
- debt > 10 bits and growing with cohort size: structural failure, replace the rule

---

## Recipe 7 — Build the case for replacing an expert rule

You will sometimes audit a rule and conclude it should be replaced. Build the case systematically:

1. **Document the structural failures** from the audit report. List the flagged tests with raw numbers.

2. **Pull the empirical external-validation literature.** Search for "rule_name external validation," "rule_name AUC," "rule_name calibration." Compile a table of AUC values across cohorts.

3. **Show the connection.** Argue that the structural failures predict the empirical inconsistency. This is the strongest form of the argument — show that the structural pathology *explains* the empirical observation.

4. **Propose the replacement.** Either a fitted alternative (RiskSLIM, AutoScore, ShapleyVIC-derived) or a structural revision (consolidated drivers, additional categories, mechanism-specific sub-rules).

5. **Argue the cost-benefit.** Interpretability vs. accuracy. Clinical acceptance vs. statistical performance. The structurally clean replacement may be harder to deploy if clinicians prefer the familiar rule; the structurally flawed incumbent may have ten years of trained intuition behind it.

This is the workflow for the methods paper's discussion section. It's also the workflow for any future "audit and replace" paper you write.

---

## Recipe 8 — Add a rule the package doesn't have yet

See `ADDING_A_RULE.md` for the full guide. Quick version:

```
ruleaudit/rules/your_rule.py     ← 30 lines, the rule definition + sanity tests
ruleaudit/samplers.py            ← add a sampler if your population differs
examples/your_rule/run.py        ← 20 lines, the runner
tests/test_your_rule.py          ← 10 sanity tests against published reference cases
```

After running, save the report to `audits/YYYY-MM-DD_your_rule.md`.

---

## Recipe 9 — Cite the package properly

In a paper:

> Sour B. RuleAudit: a data-free structural audit protocol for expert-derived clinical decision rules. Software version 0.2.0, 2026. Available at https://github.com/sourbehnam1374-beep/ruleaudit. Zenodo DOI: [pending].

In code:

```python
"""
This analysis uses ruleaudit v0.2.0 (Sour 2026).
https://github.com/sourbehnam1374-beep/ruleaudit
"""
```

The package's `CITATION.cff` will auto-populate the GitHub "Cite this repository" button after the first release.

---

## Recipe 10 — When you forget what you were doing

You'll come back to this in three months. You'll forget. Read these files in order:

1. `archive/docs/RESUME_HERE.md` — where the project stands right now, what's next
2. `archive/docs/journal.txt` — chronological log of major sessions and decisions
3. `docs/METHODOLOGY.md` — what the six tests are and why
4. `docs/INTERPRETING_REPORTS.md` — how to read an audit report
5. `audits/` — the library of audits you've completed

That's the path from "I forgot" to "OK, I remember" in 15 minutes.

---

*Revision history: v0.2 (2026-05) — full rewrite around the rules/, samplers/, audits/ structure. v0.1 — initial recipes.*
