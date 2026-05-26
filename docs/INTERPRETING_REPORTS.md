# Interpreting RuleAudit Reports

When `render_report()` writes a report.md, you get a flag-by-flag summary plus raw CSVs and figures. This guide tells you what each flag *means* clinically and what action it suggests.

This complements `METHODOLOGY.md` (which defines the tests formally). Read that first if you haven't.

---

## The report at a glance

A typical report has this shape:

```
# RuleAudit Report: [Rule Name]
Date: 2026-MM-DD
N samples: 10,000

## Test I — Firing rates
| driver | firing_rate | flag |
|---|---|---|
| ...

## Test II — Orthogonality
[heatmap + table of |r| > 0.3 pairs]

## Test III — VIF
[bar chart + table]

## Test IV — Sensitivity
[OAT plots + Sobol bar chart]

## Test V — Identifiability
[diversity plot + table]

## Test VI — MDL calibration debt (if cohort provided)

## Summary
- N flags raised: 12
- Most severe: [flag name]
- Recommendation: [action]
```

---

## Flag interpretations

### Test I flags

**`dead` (firing_rate == 0)**
- What it means: This rule cannot fire under any input combination in the realistic population.
- Why it happens: Often, the trigger condition involves a combination of inputs that is anatomically or physiologically impossible. SHIVA SPIN-THA's `low_sit_av_hyper` driver is dead because hyper-mobile patients' posterior pelvic tilt in sitting always produces functional anteversion above the trigger threshold.
- What to do: Either remove the rule (it adds complexity without information) or revisit the trigger threshold. If the rule's intent is "very rare extreme situation," verify the threshold matches the intent.

**`unreachable` (0 < firing_rate < 0.01)**
- What it means: The rule fires only in tail cases (< 1% of the realistic population).
- Why it happens: Trigger threshold set too aggressively, or the rule targets a very rare phenotype.
- What to do: Usually keep the rule (rare cases matter clinically) but flag that this rule contributes essentially nothing to score variance in modal patients. Consider whether the rule's weight is calibrated for its actual firing population (rare cases) or for the modal patient (most of the time).

**`indiscriminate` (firing_rate > 0.90)**
- What it means: The rule fires in >90% of cases. It cannot distinguish patients within the population.
- Why it happens: Trigger threshold set too leniently. SHIVA's `PI − LL > 10°` fires in 76% of synthetic cases because 10° is a low threshold for an ASD-realistic population.
- What to do: Raise the threshold to a value that produces a more informative firing rate (target 30–70%), or move the rule's signal into a graduated multi-bucket structure.

---

### Test II flags

**`collinear` (|r| > 0.95)**
- What it means: Two drivers fire under near-identical conditions. The rule double-counts one underlying signal.
- Why it happens: The two drivers' trigger conditions are mathematically equivalent (or nearly so) once you trace through the input distributions.
- What to do: Remove one of the two drivers, or merge them into a single weighted driver. Recalibration cannot fix this — only structural revision can.

**Critical case: |r| == 1.00.** The drivers are mathematically identical. The score has fewer effective dimensions than its driver count suggests. SHIVA SPIN-THA has two such pairs: ΔSS·stiff ↔ mobility·stiff and ΔSS·hyper ↔ mobility·hyper. Each pair inflates the score by the redundant weight (30 and 26 points respectively).

**`correlated` (0.7 < |r| < 0.95)**
- What it means: Substantial activation overlap. Not quite duplicate, but worth reviewing.
- Why it happens: The two drivers share most of their firing conditions but differ in edge cases.
- What to do: Investigate the edge cases. If they represent meaningful clinical distinctions, keep both drivers (this is acceptable structural correlation). If they represent measurement noise, consider merging.

---

### Test III flags

**`unidentifiable` (VIF > 5)**
- What it means: The driver's contribution to the total score is statistically tangled with the other drivers' contributions.
- Why it happens: The driver fires in a pattern that is largely predictable from the other drivers' firing patterns.
- What to do: If the rule's weights are fixed (expert-derived), VIF just diagnoses the redundancy — the rule is paying weight points for signal that's already counted. Consider whether the driver adds anything to a model trained on the other drivers.

**`extreme` (VIF > 10 or → ∞)**
- What it means: The driver is essentially a deterministic function of the other drivers. Linear dependence.
- Why it happens: Either two drivers fire under identical conditions (see `collinear` in Test II), or a combination of three or more drivers always sums to a constant.
- What to do: This is a structural error in the rule's definition, not a tuning issue. Remove the dependent driver. Note: VIF → ∞ is mathematically equivalent to "the rule has fewer effective dimensions than driver count."

---

### Test IV flags

**`inert` (OAT response is constant across input range)**
- What it means: Moving this input across its entire physiologic range does not change the total score, from the reference seed.
- Why it happens: The input is either downstream of an already-saturated driver, or its threshold is outside the physiologic range, or it never reaches any driver's trigger condition from the chosen reference seed.
- What to do: Investigate from multiple reference seeds. If inert from all seeds, the input is not actually used by the rule — flag this strongly because it means clinicians collecting this input are wasting effort. SHIVA SPIN-THA has two such inputs: `pt_standing` and `cup_inclination`.

**`step-shaped` (OAT response has sharp jumps at bucket boundaries)**
- What it means: The rule responds only to threshold crossings, not to continuous input variation.
- Why it happens: This is the *intended* behaviour of binary-driver rules. Every expert-derived integer-additive rule has step-shaped OAT.
- What to do: Note it; it's not pathological by itself. The flag is informative when paired with mechanism collapse: step-shaped + high diversity at totals tells you the rule's response is brittle to small input variations.

**`hidden_interaction` (S_T > 3 · S_1)**
- What it means: This input acts primarily through interactions with other inputs, not through a direct main effect. OAT analysis would miss this.
- Why it happens: The input appears in multiple driver trigger conditions, or it appears in an ideal-target formula that multiple drivers depend on.
- What to do: Document this as a sensitivity-fragility point. A small measurement error in such an input can move multiple drivers across bucket boundaries at once. In GAP, pelvic incidence has S_1 = 0.02 and S_T = 0.36 — PI does not vote directly but shifts three ideal-target formulae.

**`low_influence` (S_T < 0.05)**
- What it means: This input contributes less than 5% of total score variance (including all its interactions).
- Why it happens: The input is genuinely not influential in the rule.
- What to do: Decide whether to keep it. Sometimes low-influence inputs are required clinical context (age in GAP has S_T ≈ 0.04 but is clinically essential). Sometimes they are decoration.

---

### Test V flags

**`mechanism_sprawl` (> 20 distinct patterns at a category boundary)**
- What it means: At this total score, dozens of mechanistically distinct combinations of drivers all produce the same label. The label is summing too many different things.
- Why it happens: The rule has too few categories for the diversity of mechanisms its drivers can express.
- What to do: This is the structural signature of inconsistent external validation. Different cohorts will contain different mixtures of the underlying mechanisms, so no single outcome relationship can fit them all. Consider either: (a) adding more category boundaries to subdivide, or (b) modeling outcomes per-mechanism rather than per-label.

**Worked example.** GAP at total = 6 has 39 distinct patterns across 1,272 cases. The MD label at the SD boundary collapses 39 mechanisms into one category. This explains GAP's AUC range 0.50–0.86 across cohorts: each cohort gets a different mix of the 39 mechanisms.

**`mechanism_erasure` (one label > 30% of cases with ≤ 2 patterns)**
- What it means: One label encodes a huge fraction of all cases but with almost no internal variation. The label says "this case is in this category" and not much else.
- Why it happens: The rule's drivers fail to differentiate within the label. The "safe" or "low risk" or "P" label spans too much anatomical territory.
- What to do: This is the structural signature of low predictive power. The rule cannot stratify risk *within* the dominant label. Either add new drivers that differentiate within the label, or accept that this rule's positive predictive value is bounded above by the within-label mechanism heterogeneity.

**Worked example.** Lewinnek at total = 0 has 5,285 cases (52.9% of the population) collapsed into 1 firing pattern. The SAFE label encodes essentially zero information about the cup's actual position within the 400 square-degree safe zone. This explains Abdel 2016's finding that 58% of dislocated THAs are within the safe zone.

---

### Test VI flags

**`debt_positive` (calibration_debt > 0)**
- What it means: The expert rule pays more bits to predict outcomes than a simpler L1-regularised regression would.
- Why it happens: The expert rule is encoding-inefficient — its structure carries information the outcomes don't reward, or it misses information the outcomes do reward.
- What to do: Consider whether the rule is worth keeping as-is. If calibration_debt is small (a few bits), the expert rule's interpretability may be worth the inefficiency. If calibration_debt is large (tens of bits), the rule is competing with a much simpler regression and losing.

**`debt_growing` (calibration_debt grows with cohort size)**
- What it means: The inefficiency is structural, not sampling noise. As more cohort data become available, the regression's advantage grows.
- Why it happens: The expert rule has a fundamental mismatch between its structure and the outcome data. This is what Soroceanu 2015 found for the Schwab modifiers — the rule's structure doesn't match the outcome distribution.
- What to do: This is the strongest argument for replacing the expert rule with a data-derived alternative (RiskSLIM, AutoScore). The expert rule will never close the gap.

---

## How to read a report holistically

After processing flag-by-flag, ask three integrative questions:

**Q1: What is this rule's structural failure mode in one sentence?**

If you can answer, you have understood the rule. If not, re-read the flags.

Examples:
- "SHIVA SPIN-THA double-counts mobility-vs-stiffness signals through redundant driver pairs, has one unreachable rule, and has two clinically-named inputs that do not actually move the score."
- "GAP has mechanism sprawl at the MD/SD boundary — 39 distinct patterns at total = 6 — combined with hidden sensitivity load on pelvic incidence."
- "Lewinnek is structurally pristine but predictively empty — the SAFE label encodes 5,285 cases in 1 pattern."

**Q2: What's the most clinically dangerous flag?**

Rank by clinical consequence, not by p-value or VIF magnitude:
- A `dead` rule is structurally embarrassing but clinically inconsequential (it doesn't fire so it can't mislead).
- An `indiscriminate` rule firing in 80% of cases is clinically misleading — it suggests action when no action is differentiated.
- A `mechanism_erasure` flag on the dominant label is the most clinically dangerous: the rule reassures the clinician with a label that means almost nothing.

**Q3: What action does this audit recommend?**

Three categories of recommendation:
- **Revise structure** — collinear drivers, dead rules, inert inputs. Structural revision is required; recalibration won't help.
- **Recategorise** — mechanism sprawl. Add category boundaries or model per-mechanism.
- **Replace or augment** — mechanism erasure, growing MDL debt. The rule is fundamentally limited; consider a data-derived alternative or additional differentiating drivers.

---

## What flags do *not* tell you

1. **They don't tell you the rule is wrong clinically.** A rule that passes all six tests can still encode bad clinical judgment. A rule that fails all six can still be clinically useful in narrow contexts.

2. **They don't tell you whether to deploy.** Deployment decisions require regulatory review, prospective validation, and clinician acceptance. The audit is one input to the decision, not the decision itself.

3. **They don't tell you which fix to apply.** The audit shows *what* is structurally wrong; you decide *how* to address it. The same flag can suggest different fixes depending on the rule's purpose.

---

## Save your audits

Every audit you run should be saved as a permanent record. The pattern:

```
audits/
  2026-05-25_gap_v1.md         ← from `cp examples/gap/out/report.md audits/2026-05-25_gap_v1.md`
  2026-05-25_lewinnek.md
  2026-05-25_shiva_spintha_v7_4.md
  2026-06-12_sofa.md            ← future audits
  ...
```

After three months you'll have a library of audited rules. After a year, that library is your evidence base for any methods paper, talk, or grant application. Build the habit now.

---

*Revision history: v0.2 (2026-05) — added GAP and Lewinnek-specific worked examples in flag interpretations. v0.1 — initial release.*
