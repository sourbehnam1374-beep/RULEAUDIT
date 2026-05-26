# RuleAudit Methodology

This document defines the six tests of the RuleAudit protocol formally. It is intended as a reference for your future self — when you come back to this library in three months and need to remember exactly what each test measures, what the default thresholds are, and how to interpret the output.

For the philosophical motivation, see the manuscript draft in `archive/manuscript/`. For practical instructions on adding a new rule, see `ADDING_A_RULE.md`. For interpretation of completed audit reports, see `INTERPRETING_REPORTS.md`.

---

## Scope

RuleAudit applies to **rule-based, integer-additive clinical scores with discrete category outputs**. Formally:

A *rule* is a deterministic function R: X → (D, T, C) where:
- X is a structured input vector (e.g., spinopelvic parameters)
- D = {d_1, ..., d_k} is a vector of binary driver activations (1 = driver fires, 0 = silent)
- T = Σ w_i · d_i is the integer total score, with integer weights w_i
- C is a categorical label assigned by T-band cutoffs

Examples in current orthopedic practice:
- GAP (Yilgor 2017): 5 drivers, weights 1–3, total 0–13, three categories (P/MD/SD)
- Lewinnek (1978): 4 decomposed drivers, weight 1 each, total 0–2, three categories (SAFE/MIXED/UNSAFE)
- SHIVA SPIN-THA (Sour 2026): 11 drivers + 2 modifiers, weights 4–30, total 0–~130, three categories (CLEAR/WATCH/HIGH)

Rules outside this scope (continuous-output regressions, neural networks, decision trees with non-additive structure) require adaptation of Tests V and VI.

---

## The six tests

### Test I — Driver firing rates

**What it measures.** For each driver d_i, the fraction of synthetic cases in which d_i fires:

    firing_rate(d_i) = (1/N) · Σ_j d_i(x_j)

over N samples drawn from a realistic input distribution.

**Default flags.**
- `dead`: firing_rate == 0.000 (the rule cannot fire under any input)
- `unreachable`: 0 < firing_rate < 0.01 (the rule requires inputs at the tail of the physiologic distribution)
- `indiscriminate`: firing_rate > 0.90 (the rule fires too readily to discriminate)

**Interpretation.**
- A dead rule is unreachable code. It should be removed or its trigger condition revisited.
- An unreachable rule may still be correct but it conveys no information in the modal population.
- An indiscriminate rule reduces the score's effective dynamic range; consider raising the trigger threshold.

**Information-theoretic basis.** A binary indicator's entropy H(p) = -p log p - (1-p) log(1-p) is maximised at p = 0.5 and approaches zero at the extremes. The default 0.01 / 0.90 flags correspond to entropies below 0.08 bits — the indicator carries less than one-eighth of a bit of information per case, regardless of its weight.

---

### Test II — Driver orthogonality

**What it measures.** Pearson and Spearman correlation matrices over the binary driver activations:

    r_ij = corr(d_i(x), d_j(x))   for all i ≠ j

across N samples.

**Default flags.**
- `collinear`: |r_ij| > 0.95 (the two drivers fire under near-identical conditions)
- `correlated`: 0.7 < |r_ij| < 0.95 (substantial overlap, candidate for review)

**Interpretation.** Two drivers with r_ij = 1.00 fire under mathematically equivalent conditions. The rule double-counts one underlying signal. This cannot be repaired by recalibration — the redundant driver must be removed or merged.

**Critical case.** When r_ij = 1.00 *exactly*, this indicates that the firing condition for d_i is a deterministic function of the firing condition for d_j. This is structurally identical to renaming the same indicator twice; it inflates the total score by the redundant weight.

---

### Test III — Variance inflation factor (VIF)

**What it measures.** For each driver d_i, the VIF is computed by regressing d_i on the other drivers:

    VIF(d_i) = 1 / (1 - R²_i)

where R²_i is the coefficient of determination from regressing d_i on {d_j : j ≠ i}.

**Default flags.**
- `unidentifiable`: VIF > 5
- `extreme`: VIF > 10 or VIF → ∞ (numerically infinite, indicating exact linear dependence)

**Interpretation.** High VIF means the driver's contribution to the total score is statistically unidentifiable from the contributions of other drivers. If you were to fit the weights to outcome data, the inflated variance of the estimated weight would make the rule unstable under resampling. For expert-derived rules where the weights are fixed by consensus rather than fitted, VIF still diagnoses redundancy: the rule is paying multiple weight points for what is effectively one signal.

**Relationship to Test II.** VIF and pairwise correlations are complementary. A driver can have moderate pairwise correlations with multiple other drivers but still have very high VIF (multicollinearity that no single pair captures). Conversely, two perfectly collinear drivers will both have VIF → ∞ but the pairwise correlation will show only one r = 1.00 cell.

---

### Test IV — Sensitivity analysis

Two sub-tests.

**Test IV-a: One-at-a-time (OAT) sweeps.** For each input variable, sweep across its physiologic range while holding all other inputs at reference values. Plot total score as a function of the swept variable.

**Default flags.**
- `inert`: total score does not change across the input's full range (the input does not influence the score from this seed point)
- `step-shaped`: total score is piecewise constant with sharp jumps at bucket boundaries (the rule responds only to threshold crossings, not to continuous input variation)

**Test IV-b: Sobol global sensitivity indices.** First-order index S_1 (the input's direct effect on score variance) and total-order index S_T (direct effect plus all interactions) for each input.

**Default flags.**
- `hidden_interaction`: S_T > 3 · S_1 (the input acts primarily through interactions, hidden in OAT sweeps)
- `low_influence`: S_T < 0.05 (the input contributes less than 5% of total score variance, including all interactions)

**Interpretation.** OAT sweeps detect inert inputs and identify the rule's local response shape. Sobol decomposition detects global structure: variables that look unimportant in OAT (small S_1) but actually shift many drivers at once (large S_T) are hidden fragility points. A 5° measurement error in such a variable can move multiple drivers across bucket boundaries simultaneously.

**Worked example.** In GAP, pelvic incidence (PI) has S_1 ≈ 0.02 and S_T ≈ 0.36. PI does not vote directly into the score, but it shifts three ideal-target formulae (for SS, LL, and GT) simultaneously. OAT analysis would miss this; Sobol catches it.

---

### Test V — Combinatorial identifiability

**What it measures.** For each value t of the total score, count the number of distinct driver-firing patterns producing that total:

    patterns(t) = |{(d_1, ..., d_k) : T(d) = t and (d_1, ..., d_k) appears in the synthetic sample}|

and the diversity ratio:

    diversity(t) = patterns(t) / cases(t)

**Default flags.**
- `mechanism_sprawl`: patterns(t) > 20 at a category boundary (multiple distinct mechanisms collapse to the same label)
- `mechanism_erasure`: cases(t) / N > 0.3 with patterns(t) ≤ 2 (one label encodes a large fraction of all cases, with little internal variation)

**Interpretation.** Mechanism sprawl is the structural signature of inconsistent external validation: different cohorts contain different mixtures of the underlying mechanisms, so no single outcome relationship can fit them all. Mechanism erasure is the structural signature of low predictive power: when a label spans many anatomical configurations, the label cannot stratify risk within itself.

**Critical case.** Pattern counts at category boundaries (the highest total in one category, the lowest total in the next) are the most diagnostic. A clinically used label that contains 40 distinct mechanisms at the boundary will fail to generalise consistently.

**Implementation note.** Patterns are deduplicated using the tuple of driver activations. With k drivers, the theoretical maximum is 2^k distinct patterns, but the actual maximum in the synthetic sample depends on which combinations are reachable from realistic inputs.

---

### Test VI — MDL calibration debt

**The only outcome-dependent test.** Requires a labelled cohort (X, y) where y is a binary outcome.

**What it measures.** Two-part minimum description length:

    L_total(M, D) = L(M) + L(D | M)

where:
- L(M) is the code length of the rule structure (driver definitions, weights, cutoffs)
- L(D | M) is the code length of the residual prediction errors on the labelled cohort

We compare the expert rule against the best L1-regularised logistic regression baseline trained on the same input features:

    calibration_debt = L_total(M_expert, D) - L_total(M_baseline, D)

**Default flags.**
- `debt_positive`: calibration_debt > 0 (the expert rule pays more bits than a regression would)
- `debt_growing`: calibration_debt grows with cohort size (structural inefficiency, not sampling noise)

**Interpretation.** Calibration debt is the bit-level analog of "outcome-fit gap": how many bits the rule wastes by being expert-derived rather than data-derived. Negative or zero debt means the expert rule is competitive with the best regression. Positive debt means the expert rule could be replaced by a simpler regression with no loss of fit. Growing debt with cohort size means the expert rule's structural inefficiency does not wash out — it is a permanent feature of the rule, not a small-sample artifact.

**When to skip this test.** Skip Test VI when (a) no labelled cohort is available, (b) the rule is structurally so flawed (per Tests I–V) that calibration is irrelevant, or (c) the rule is being evaluated for replacement rather than for repair. The other five tests are sufficient for the most common audit purposes.

---

## Default thresholds — summary

| Test | Flag | Default threshold | Rationale |
|------|------|-------------------|-----------|
| I    | dead | firing == 0 | Unreachable code |
| I    | unreachable | firing < 0.01 | Tail-only activation |
| I    | indiscriminate | firing > 0.90 | Discriminatory failure |
| II   | collinear | \|r\| > 0.95 | Effective duplicate |
| II   | correlated | 0.7 < \|r\| < 0.95 | Substantial overlap |
| III  | unidentifiable | VIF > 5 | Statsmodels convention |
| III  | extreme | VIF > 10 or ∞ | Exact linear dependence |
| IV   | inert | OAT range == 0 | Locally unused |
| IV   | hidden_interaction | S_T > 3 · S_1 | Indirect effect ≫ direct |
| IV   | low_influence | S_T < 0.05 | <5% variance contribution |
| V    | mechanism_sprawl | patterns > 20 at boundary | Inconsistent external validation |
| V    | mechanism_erasure | one label > 30% of cases with ≤2 patterns | Low information per label |
| VI   | debt_positive | calibration_debt > 0 | Encoding-inefficient rule |

These thresholds are tuned defaults from the SHIVA, GAP, and Lewinnek audits. They are intended as starting values, not as rigid bars. The audit reports always show the raw numbers; the flags are interpretive aids, not verdicts.

---

## What this protocol does *not* claim

1. **It does not claim outcome-dependent failure is solely structural.** A rule with no structural pathologies can still fail external validation due to derivation-cohort bias, sample size, or genuine population differences. RuleAudit catches structural failure; it does not rule out other failure modes.

2. **It does not claim structural soundness implies clinical utility.** A rule can pass all six tests and still be clinically useless if the underlying biology doesn't support the rule's mechanism. RuleAudit checks the rule's internal consistency, not the rule's biological validity.

3. **It does not claim AI-only validation is sufficient.** Peer review, clinical trials, and prospective validation remain essential. RuleAudit is a *pre-deployment structural check*, not a replacement for any of those.

4. **It does not claim its default thresholds are universal.** The thresholds in the table above are tuned from three orthopedic worked examples. They may need adjustment for rules in other clinical domains (ICU scores, oncology risk scores, cardiology). Future revisions of this document will track threshold calibration as more rules are audited.

---

*Revision history: v0.2 (2026-05) — added Lewinnek findings, corrected LDI scoring per Yilgor 2017 verification. v0.1 (2026-05) — initial release.*
