# RuleAudit cookbook

These recipes use the version 0.2.1 API. Interpret every result within the limits in `METHODOLOGY.md`.

## 1. Run a packaged example

```bash
python examples/gap/run.py
```

This writes a Markdown report, CSV tables, and PNG figures under `examples/gap/out/`. The directory is ignored by Git so generated artifacts do not become stale repository links.

The CLI can run a script that exposes a module-level `audit` object:

```bash
ruleaudit run examples/gap/run.py --out ruleaudit_out --n-random 10000 --n-saltelli 512
```

## 2. Create a minimal rule

```python
from ruleaudit import InputSpec, InputVar, RuleAudit, render_report

def rule(inputs):
    drivers = {
        "a_high": 2 * int(inputs["a"] > 10),
        "b_low": int(inputs["b"] < 0),
    }
    total = sum(drivers.values())
    return {
        "drivers": drivers,
        "total": total,
        "category": "LOW" if total == 0 else "ELEVATED",
    }

spec = InputSpec(vars=[
    InputVar("a", 0, 20),
    InputVar("b", -5, 5),
])

audit = RuleAudit(rule=rule, input_spec=spec, seed=42)
result = audit.run(n_random=10_000, n_saltelli=512)
render_report(result, "out", title="Example rule")
```

The `drivers` values are numeric score contributions. The firing-rate test treats any contribution greater than zero as active, and the pattern-multiplicity test casts contributions to integers.

## 3. Supply a correlated random-sweep sampler

A joint sampler receives a NumPy random generator and returns one input dictionary:

```python
def correlated_sampler(rng):
    a = float(rng.normal(10, 2))
    b = float(0.5 * a + rng.normal(0, 1))
    return {"a": a, "b": b}

audit.input_spec.joint_sampler = correlated_sampler
```

The random sweep will use this sampler. The Sobol routine will still use independent uniform draws over the `InputSpec` bounds. Report those two analysis targets separately.

## 4. Compare sampler assumptions

Create a fresh audit object for each run so that the random generator starts from the same seed:

```python
from copy import deepcopy
from ruleaudit import RuleAudit
from ruleaudit.rules import gap
from ruleaudit.samplers import asd_realistic

def run_with(sampler):
    spec = deepcopy(gap.spec)
    spec.joint_sampler = sampler
    audit = RuleAudit(
        gap.rule,
        spec,
        driver_names=gap.metadata["driver_names"],
        seed=42,
    )
    return audit.run(n_random=10_000, seeds=gap.seeds, n_saltelli=512)

literature_informed = run_with(asd_realistic)
independent_uniform = run_with(None)
```

Compare raw firing rates, correlations, VIFs, and pattern counts. A difference is evidence of assumption sensitivity, not proof that one sampler is clinically correct.

## 5. Inspect driver-pattern multiplicity

```python
table = result.identifiability.per_total
print(table[["total", "n_cases", "n_patterns", "diversity_ratio"]])
```

The legacy `identifiability` name is retained for API compatibility. Counts are sample-dependent. Repeat with larger samples and alternative samplers before discussing them, and avoid translating the heuristic flags into predictive or mechanistic conclusions.

## 6. Use OAT results

```python
seeds = {
    "reference": {"a": 10.0, "b": 0.0},
    "edge": {"a": 9.9, "b": -0.1},
}
result = audit.run(n_random=10_000, seeds=seeds)
print(result.sensitivity.oat.head())
```

An OAT path varies one input while holding all other values at the selected seed. Repeat meaningful seeds; a flat path at one seed is only a local observation.

## 7. Treat the MDL module as experimental

The optional `mdl_inputs=(y, raw_input_columns, L_M_expert)` interface evaluates outcomes against the internally generated random sweep. It does not provide a validated external-cohort workflow, cross-validation, uncertainty estimates, or an objective rule-code-length estimator. Use it only for development experiments where `y` is deliberately aligned with the generated sweep, and do not use its result as a clinical replacement decision.

## 8. Save a reproducible analysis

Alongside exported CSVs and plots, record:

- the RuleAudit version and dependency environment;
- rule source and implementation revision;
- bounds and joint-sampler code;
- seed, random-sweep size, and Sobol base sample size;
- OAT seeds and threshold overrides;
- which findings came from the joint-sampled sweep versus independent-uniform Sobol analysis.

## 9. Cite the software

Use `CITATION.cff` or this plain-text form:

> Sour B. RuleAudit (version 0.2.1) [Computer software]. https://github.com/sourbehnam1374-beep/ruleaudit
