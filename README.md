# ruleaudit

**A data-free structural audit protocol for expert-derived clinical decision rules.**

Six computational tests for any rule-based, integer-additive clinical score (orthopedic, sepsis, trauma, surgical risk). Five tests require no patient data. Run before deployment or validation to catch structural pathologies that no outcome study can fix.

## Why

Most clinical decision rules in use today are expert-derived: features and weights set by consensus, not regression. When they fail external validation, investigators usually scrutinize the data. We argue the *structure* should be scrutinized first. A rule whose drivers are perfectly collinear cannot be saved by recalibration. A rule that fires in 0% or 100% of cases conveys no information regardless of how it is weighted. A rule whose category boundaries collapse dozens of distinct mechanisms into a single label will fail to generalize for reasons no outcome study can repair.

## What it does

| Test | What it detects | Outcome data required? |
|---|---|:---:|
| 1. Firing rates | dead rules, always-on rules | No |
| 2. Driver orthogonality | collinear drivers, double-counting | No |
| 3. Variance inflation | unidentifiable contributions | No |
| 4. Sensitivity (Sobol + OAT) | inert inputs, hidden interaction load | No |
| 5. Identifiability | mechanism collapse at score boundaries | No |
| 6. MDL calibration debt | encoding inefficiency vs L1 baseline | Yes |

Produces a markdown report with figures, CSVs, and a flagged-issue summary.

## Install

```bash
pip install -e .
```

## Quickstart

A rule is any Python callable that takes a dict of inputs and returns a dict with `drivers` and `total`:

```python
from ruleaudit import RuleAudit, InputSpec, InputVar, render_report

def my_rule(inp):
    drivers = {
        "high_bp": 1 if inp["sbp"] > 140 else 0,
        "old":     1 if inp["age"] > 65  else 0,
    }
    return {"drivers": drivers, "total": sum(drivers.values())}

spec = InputSpec(vars=[
    InputVar("sbp", 90, 200),
    InputVar("age", 18, 90),
])

audit = RuleAudit(rule=my_rule, input_spec=spec)
result = audit.run(n_random=10_000)
render_report(result, "out/")
```

Or run an included example:

```bash
python examples/gap/run.py
python examples/shiva/run.py
```

## Worked examples

Two are bundled: the GAP score (Yilgor 2017, ASD planning) and SHIVA SPIN-THA v7.4 (a deterministic spinopelvic risk score for total hip arthroplasty). Together they demonstrate that RuleAudit produces non-overlapping failure signatures: GAP fails the sensitivity and identifiability tests but passes everything else; SHIVA fails the firing, orthogonality, VIF, and sensitivity tests with different patterns.

## Status

Alpha. The protocol is described in [manuscript title TK]. The Python API is stable for the six tests; CLI and report rendering may change.

## License

MIT.
