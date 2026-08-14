# RuleAudit methodology

This document describes what version 0.2.1 computes. RuleAudit is a descriptive screening workflow for deterministic additive scores. It does not test predictive validity, calibration, clinical utility, causality, or safety.

## Analysis boundary

A compatible rule accepts a dictionary of inputs and returns:

```python
{
    "drivers": {"driver_name": contribution, ...},
    "total": numeric_total,
    "category": "optional label",
}
```

An `InputSpec` defines each input's lower and upper bounds and may define a `joint_sampler`. The random sweep uses that joint sampler when present. All random-sweep diagnostics are conditional on its assumptions, the seed, and the number of synthetic cases.

The Sobol calculation has a different sampling boundary: version 0.2.1 uses independent uniform sampling over the `InputSpec` bounds. It does not use or preserve a configured joint sampler's correlations. OAT results are conditional on the supplied seed cases.

## 1. Driver firing rates

For each driver, RuleAudit reports:

- `fire_rate`: the fraction of synthetic cases for which the contribution is greater than zero;
- `mean_contrib`: the mean numeric driver contribution.

Default heuristic flags are:

- `DEAD`: firing rate equals 0;
- `RARE`: firing rate is below 0.01 but greater than 0;
- `ALWAYS-ON`: firing rate is greater than 0.90.

These labels describe the configured synthetic sweep. A `DEAD` result does not prove that activation is impossible outside the sampled distribution, and a rare activation is not necessarily erroneous.

## 2. Driver correlations

RuleAudit computes Pearson and Spearman correlations among nonconstant driver-contribution columns. It reports Pearson pairs whose absolute correlation exceeds 0.50 and labels pairs at or above 0.95 as `EXTREME-COLLINEAR`.

Correlation describes co-activation in the configured sweep. Even a sample correlation of 1.0 is not, by itself, a proof that two rule expressions are mathematically identical over every valid input.

## 3. Variance inflation factors

For every nonconstant driver-contribution column, RuleAudit calculates the conventional variance inflation factor after adding an intercept. The default report labels values above 5 as `HIGH-VIF` and values above 100 or infinity as `EXTREME-VIF`.

This is a linear-dependence diagnostic for the sampled driver matrix. It does not estimate clinical effects or identify a driver's causal contribution. The thresholds are review heuristics, not validated clinical cutoffs.

## 4. Sensitivity analysis

### One-at-a-time sweeps

For every named seed case, each input is varied across its full `InputSpec` range while the other inputs remain fixed at that seed. The resulting total score is saved to `oat.csv` and plotted. This is a local, seed-dependent description; a flat path from one seed does not establish global irrelevance.

### Sobol indices

RuleAudit uses SALib to estimate first-order (`S1`) and total-order (`ST`) Sobol indices for the total score. Version 0.2.1 samples the declared bounds independently and uniformly. Indices therefore describe that configured rectangular envelope, not a clinical population and not the correlated random-sweep sampler.

The implementation reports:

- `INTERACTION-DOMINATED` when `ST > 0.05` and `(ST - S1) / ST > 0.50`;
- `INERT` when `ST < 0.005`.

Monte Carlo estimates can be noisy, including slightly negative first-order estimates or uncertainty intervals that overlap zero. A sensitivity result does not demonstrate measurement-error harm, category instability in patients, or clinical importance without a separate analysis designed for that question.

## 5. Driver-pattern multiplicity

The public API retains the legacy method name `test_identifiability`, result field `identifiability`, and file name `identifiability.csv`. The implemented calculation is not a formal identifiability test.

For each sampled total score with at least five cases, RuleAudit counts:

- `n_cases`: sampled cases with that total;
- `n_patterns`: distinct integer-cast driver-contribution tuples observed at that total;
- `diversity_ratio`: `n_patterns / n_cases`.

The current report generator emits descriptive heuristic labels:

- `LOW-PATTERN-RATIO` when `n_cases >= 100` and `diversity_ratio < 0.02`;
- `HIGH-PATTERN-MULTIPLICITY` when `n_cases >= 200` and `diversity_ratio > 0.025`.

Both the count and ratio depend on sample size, sampler support, driver encoding, and score weights. A low ratio can arise mechanically as repeated cases accumulate. These outputs are descriptive prompts for reviewing within-total compression; they do not prove a mechanism, predict external validation, or establish that a category should be changed.

## 6. Exploratory MDL comparison

This optional module requires a binary outcome vector, raw input-column names, and a caller-supplied estimate of the rule's model code length (`L_M_expert`). It compares:

1. the supplied rule code length plus the empirical conditional entropy of the outcome given the total score; and
2. a standardized L1-logistic model selected from a fixed `C` grid, with a simple coefficient-count code-length penalty and in-sample log loss.

Version 0.2.1 does not cross-validate this comparison, quantify uncertainty, correct for model selection, or provide a validated method for choosing `L_M_expert`. The result is an experimental implementation detail, not evidence that a clinical rule should be retained, replaced, or deployed.

## Reproducibility

`RuleAudit(seed=...)` seeds the random sweep and Sobol routines. For a clean replay, create a new `RuleAudit` instance with the same inputs, seed, sample sizes, Python environment, and dependency versions. Reusing the same instance advances its random generator.

Generated reports include CSVs and plots, but they do not automatically record every sampler assumption or package version. A shareable analysis should also record:

- the exact rule encoding and source;
- input bounds and joint-sampler code;
- seed, `n_random`, and `n_saltelli`;
- RuleAudit and dependency versions;
- any threshold overrides;
- whether results came from the random sweep, OAT seeds, or independent-uniform Sobol sampling.

## Appropriate interpretation

RuleAudit can support code review and hypothesis generation about a rule's behavior under stated assumptions. It cannot replace reference-case verification, patient-level validation, prospective evaluation, clinical judgment, or regulatory review.
