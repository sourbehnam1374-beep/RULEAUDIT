# RuleAudit 0.2.1

RuleAudit is an alpha-stage Python workflow for **outcome-free structural screening of deterministic additive clinical scores**. It evaluates a rule under explicitly specified synthetic input distributions and reports descriptive diagnostics of driver activation, co-activation, sensitivity, and driver-pattern multiplicity.

Tests 1–5 do not require individual patient records or outcome labels. They are not “data free” in the broader sense: the rule encoding, input bounds, sampler assumptions, and any literature-informed distribution parameters are inputs to the analysis. Test 6 accepts labelled outcomes and is exploratory.

## Scope and limits

RuleAudit is intended for deterministic rules that return named driver contributions and a total score. It can help expose behavior worth reviewing, but it does **not** establish predictive accuracy, calibration, causality, clinical validity, transportability, or safety. Results are conditional on the implemented rule, the selected bounds or sampler, the seed, and the sample size.

This software is research code, not clinical decision support. Verify every rule transcription against its authoritative source before interpreting an output.

## Diagnostics

| Diagnostic | What the implementation reports | Outcome labels required? |
|---|---|:---:|
| 1. Firing rates | Frequency and mean contribution of each driver in the synthetic sweep | No |
| 2. Driver correlations | Pearson and Spearman co-activation in the synthetic sweep | No |
| 3. Variance inflation factors | Linear dependence among nonconstant driver columns | No |
| 4. Sensitivity | Seed-dependent one-at-a-time sweeps and Sobol indices over independent uniform bounds | No |
| 5. Driver-pattern multiplicity | Sampled driver-contribution patterns observed at each total score | No |
| 6. Exploratory MDL comparison | In-sample code-length comparison with an L1-logistic baseline | Yes |

For compatibility, the Test 5 API, result field, CSV, and some report labels retain the legacy name `identifiability`. The calculation is a sample-dependent pattern count; it is not a formal identifiability test. The MDL comparison uses a caller-supplied rule code length and a fixed in-sample model grid; it has not been validated as a clinical decision criterion.

The random sweep uses `InputSpec.joint_sampler` when one is supplied. The current Sobol implementation separately samples each `InputSpec` bound as an independent uniform variable and therefore does not preserve correlations from a joint sampler.

## Install

RuleAudit requires Python 3.10 or newer.

```bash
python -m pip install -e .
```

For the test suite:

```bash
python -m pip install -e ".[test]"
python -m pytest -q
```

For the exact Python 3.12.13 environment used to validate v0.2.1:

```bash
python -m pip install -r requirements-lock.txt
python -m pip install -e . --no-deps
python -m pytest -q
```

## Audit a built-in example

```python
from ruleaudit import RuleAudit, render_report
from ruleaudit.rules import gap
from ruleaudit.samplers import asd_realistic

audit = RuleAudit(
    rule=gap.rule,
    input_spec=gap.spec,
    driver_names=gap.metadata["driver_names"],
    seed=42,
)
audit.input_spec.joint_sampler = asd_realistic

result = audit.run(n_random=10_000, seeds=gap.seeds, n_saltelli=512)
render_report(result, "out")
```

The packaged examples can also be run directly:

```bash
python examples/gap/run.py
python examples/lewinnek/run.py
python examples/shiva/run.py
```

The GAP and Lewinnek modules are worked transcriptions for demonstrating the workflow. The Lewinnek example is an author-created four-boundary violation encoding of the published safe-zone rectangle. The SHIVA module is an illustrative draft-rule encoding, not independent validation of that rule.

## Audit another rule

```python
from ruleaudit import InputSpec, InputVar, RuleAudit, render_report

def my_rule(inputs):
    drivers = {
        "high_bp": int(inputs["sbp"] > 140),
        "older_age": int(inputs["age"] > 65),
    }
    return {"drivers": drivers, "total": sum(drivers.values())}

spec = InputSpec(vars=[
    InputVar("sbp", 90, 200),
    InputVar("age", 18, 90),
])

audit = RuleAudit(rule=my_rule, input_spec=spec, seed=42)
result = audit.run(n_random=10_000)
render_report(result, "out")
```

See [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) for the implemented calculations, [`docs/INTERPRETING_REPORTS.md`](docs/INTERPRETING_REPORTS.md) for bounded interpretation, [`docs/LITERATURE.md`](docs/LITERATURE.md) for literature context, and [`docs/ADDING_A_RULE.md`](docs/ADDING_A_RULE.md) for integration guidance.

Versioned example-output snapshots are included under `examples/<name>/out/`. Re-run an example to refresh its report, CSV, and figure files; interpret each snapshot with its recorded rule, sampler, bounds, seed, sample size, and software environment. The Markdown files under `audits/` are additional archived text snapshots.

## Citation

Citation metadata are provided in [`CITATION.cff`](CITATION.cff). A plain-text form is:

> Sour B. RuleAudit (version 0.2.1) [Computer software]. https://github.com/sourbehnam1374-beep/ruleaudit

## License

[MIT](LICENSE)
