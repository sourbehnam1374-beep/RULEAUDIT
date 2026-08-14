# Interpreting RuleAudit reports

A RuleAudit report is a descriptive record of one implemented rule under one configured synthetic analysis. Treat its flags as prompts for review, not pass/fail verdicts.

## Start with the analysis configuration

Before interpreting a number, record:

- the exact rule version and transcription source;
- the input bounds and random-sweep sampler;
- the random seed and sample sizes;
- the OAT seed cases;
- threshold overrides and software versions.

The random sweep may use a correlated `joint_sampler`. The current Sobol routine does not: it uses independent uniform draws over the declared bounds. Do not describe Sobol indices as population estimates unless the independent-uniform envelope itself is the intended target distribution.

## 1. Firing rates

`DEAD`, `RARE`, and `ALWAYS-ON` describe activation frequency in the sampled sweep. They can identify code or threshold behavior worth checking. They do not establish that a driver is impossible, inappropriate, or clinically uninformative outside that sweep.

Review the underlying input support first. A narrow or misspecified sampler can create any of these flags.

## 2. Correlations

High absolute correlation means two driver-contribution columns behaved similarly in the sampled cases. Inspect the rule expressions and boundary cases before calling them duplicates. Correlation is distribution-dependent, and constant columns are omitted.

## 3. VIF

VIF summarizes linear dependence among the nonconstant driver columns in the sweep. High or infinite values support a closer review of redundancy in that matrix. They do not identify causal effects, estimate weight uncertainty for a fixed score, or independently prove a coding defect.

## 4. Sensitivity

OAT paths are local to the supplied seeds. Repeat them from clinically or analytically meaningful seeds before interpreting a flat or step-shaped response.

Sobol `S1` and `ST` values describe variance in the score over independent uniform input bounds. They can be useful for code-behavior screening. They do not, without additional work, quantify patient-level importance, measurement-error fragility, outcome importance, or clinical risk. Small negative estimates can occur from Monte Carlo error.

## 5. Driver-pattern multiplicity

The section and output file retain the legacy word `identifiability`, but the calculation counts observed driver-contribution patterns per total score. `n_patterns` and `n_patterns / n_cases` vary with sample size, sampler support, encoding, and weights.

Use this table to ask questions such as:

- Which different contribution patterns reach the same total in this sample?
- Does the result change with a different sampler or larger sample?
- Is any compression a deliberate property of the scoring design?

Do not use the `LOW-PATTERN-RATIO` or `HIGH-PATTERN-MULTIPLICITY` labels as evidence of a biological mechanism, predictive failure, causal explanation, or required recategorization.

## 6. Exploratory MDL output

The optional MDL result is an in-sample comparison that depends on a caller-supplied rule code length and a fixed L1-logistic grid. It is not a validated clinical model-comparison procedure. Report it as exploratory and include the supplied code-length assumptions; do not treat its sign or magnitude as a replacement decision.

## Reading the archived examples

Markdown files in `audits/` are archived text snapshots produced by earlier runs. The referenced generated figures are not tracked in the repository, so the snapshots contain tables but no live image links. Re-run the corresponding script under `examples/` to produce a complete current report.

The packaged GAP and Lewinnek encodings are worked examples, not independently certified reference implementations. The Lewinnek example transforms the published rectangular safe zone into four boundary-violation contributions; conclusions about pattern counts are conditional on that author-created encoding. The SHIVA example is an illustrative draft-rule encoding and is not validation evidence.

## Minimum reporting language

A bounded result statement should identify the analysis boundary explicitly. For example:

> Under the specified synthetic sampler and seed, the implemented rule produced the reported driver frequencies, correlations, sensitivity indices, and within-total pattern counts. These descriptive results do not establish predictive accuracy, causality, clinical validity, or safety.

When comparing runs, show the raw values and uncertainty where available. Avoid translating heuristic flags into clinical recommendations without separate patient-level evidence.
