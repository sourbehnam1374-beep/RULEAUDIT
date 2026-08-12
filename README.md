# ruleaudit v0.2

**A data-free structural audit protocol for expert-derived clinical decision rules.**

Six computational tests for any rule-based, integer-additive clinical score. Five tests require no patient data. Run before deployment or validation to catch structural pathologies that no outcome study can fix.

## What's new in v0.2

- **`ruleaudit.rules`** — built-in library of audited rules: `gap`, `lewinnek`, `shiva_spintha`. Each module exposes `rule()`, `InputSpec`, named `seeds`, and a `metadata` block (citation, validation history, driver names).
- **`ruleaudit.samplers`** — reusable joint distributions: `asd_realistic`, `tha_realistic`, `uniform_spec`.
- **GAP score LDI bug fixed.** Verified against the actual Yilgor 2017 JBJS PDF (Fig 6 / Table IV).
- **Lewinnek safe zone added** as the second built-in worked example.
- **Reorganized examples** under `examples/{gap,lewinnek,shiva}/run.py`.

## Three failure modes the protocol catches

| Failure mode | Symptom | Example |
|---|---|---|
| Driver inflation | Drivers double-count signals; dead/always-on rules; inert inputs | SHIVA SPIN-THA v7.4 |
| Mechanism sprawl | Distinct mechanisms collapse to one label at decision boundaries | GAP (Yilgor 2017) |
| Mechanism erasure | A single label covers too much anatomy to discriminate outcomes | Lewinnek safe zone (1978) |

## The six tests

| Test | What it detects | Outcome data required? |
|---|---|:---:|
| 1. Firing rates | dead rules, always-on rules | No |
| 2. Driver orthogonality | collinear drivers | No |
| 3. Variance inflation | unidentifiable contributions | No |
| 4. Sensitivity (Sobol + OAT) | inert inputs, hidden interaction load | No |
| 5. Identifiability | mechanism collapse at score boundaries | No |
| 6. MDL calibration debt | encoding inefficiency vs L1 baseline | Yes |

## Install

```bash
pip install -e .
```

## Quickstart — audit a built-in rule

```python
from ruleaudit import RuleAudit, render_report
from ruleaudit.rules import gap
from ruleaudit.samplers import asd_realistic

audit = RuleAudit(
    rule=gap.rule,
    input_spec=gap.spec,
    driver_names=gap.metadata["driver_names"],
)
audit.input_spec.joint_sampler = asd_realistic
result = audit.run(n_random=10_000, seeds=gap.seeds)
render_report(result, "out/")
```

## Quickstart — audit your own rule

```python
from ruleaudit import RuleAudit, InputSpec, InputVar, render_report

def my_rule(inp):
    drivers = {
        "high_bp": 1 if inp["sbp"] > 140 else 0,
        "old":     1 if inp["age"] > 65  else 0,
    }
    return {"drivers": drivers, "total": sum(drivers.values())}

spec = InputSpec(vars=[InputVar("sbp", 90, 200), InputVar("age", 18, 90)])
audit = RuleAudit(rule=my_rule, input_spec=spec)
result = audit.run(n_random=10_000)
render_report(result, "out/")
```

## Examples

```bash
python examples/gap/run.py
python examples/lewinnek/run.py
python examples/shiva/run.py
```

## Citation

> Sour B. *RuleAudit: A Data-Free Structural Audit Protocol for Expert-Derived Clinical Decision Rules.* Manuscript v0.2 (May 2026).

## License

MIT.
