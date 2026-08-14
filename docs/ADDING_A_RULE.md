# Adding a rule

This guide describes the version 0.2.1 integration pattern. A successful software run does not validate a clinical rule.

## 1. Verify the encoding source

Use the authoritative publication or specification. Record the exact driver definitions, point contributions, total calculation, category boundaries, units, and boundary inclusivity. If the source is ambiguous, document the implementation choice rather than silently resolving it.

Create reference-case tests wherever the source provides worked cases or tables. If no published reference cases exist, say that the transcription has not been independently verified.

## 2. Implement the callable

```python
def rule(inputs):
    drivers = {
        "driver_1": 2 * int(inputs["input_a"] > 40),
        "driver_2": int(inputs["input_b"] < -10),
    }
    total = sum(drivers.values())
    if total <= 1:
        category = "LOW"
    elif total <= 2:
        category = "MID"
    else:
        category = "HIGH"
    return {"drivers": drivers, "total": total, "category": category}
```

Driver values should be numeric contributions to the total. `category` is optional. Keep units and inclusive/exclusive boundary choices visible in code.

## 3. Define the input specification

```python
from ruleaudit import InputSpec, InputVar

spec = InputSpec(vars=[
    InputVar("input_a", 0, 80),
    InputVar("input_b", -30, 30),
])
```

Bounds define the OAT range and the independent-uniform Sobol analysis. They should be justified as analysis assumptions; do not automatically call them physiologic or population-representative.

## 4. Add reference-case tests

```python
def test_published_case_a():
    result = rule({"input_a": 50, "input_b": -15})
    assert result["drivers"] == {"driver_1": 2, "driver_2": 1}
    assert result["total"] == 3
    assert result["category"] == "HIGH"
```

Test exact threshold values and values immediately to either side. Include the source location for each expected result in a comment or test name.

## 5. Optionally define a joint sampler

The random-sweep sampler returns one case per call:

```python
def joint_sampler(rng):
    input_a = float(rng.normal(40, 8))
    input_b = float(0.25 * input_a + rng.normal(0, 4))
    return {"input_a": input_a, "input_b": input_b}

spec.joint_sampler = joint_sampler
```

Document every distribution parameter and correlation assumption. A sampler based only on judgment is still usable for exploration, but it should not be presented as an observed clinical population.

The joint sampler affects the random sweep, firing rates, correlations, VIFs, and pattern counts. It does not affect the current Sobol calculation, which samples bounds independently.

## 6. Build and run the audit

```python
from ruleaudit import RuleAudit, render_report

seeds = {
    "reference": {"input_a": 40, "input_b": 0},
    "boundary": {"input_a": 40.01, "input_b": -10.01},
}

audit = RuleAudit(
    rule=rule,
    input_spec=spec,
    driver_names=["driver_1", "driver_2"],
    seed=42,
)
result = audit.run(n_random=10_000, seeds=seeds, n_saltelli=512)
render_report(result, "examples/your_rule/out", title="Your rule")
```

`render_report` writes `report.md`, raw CSV tables, and diagnostic PNG files. Generated example output directories are ignored by Git in this repository.

## 7. Review limitations before sharing

Confirm that:

- reference-case tests pass;
- the sampler and bounds are documented;
- results are reproducible from a fresh object with the same seed and environment;
- Test 5 is described as sample-dependent driver-pattern multiplicity despite its legacy API name;
- Sobol results are described as independent-uniform bound analysis;
- optional MDL output is labelled experimental;
- no finding is presented as predictive, causal, clinically validated, or deployment-ready without separate evidence.

Non-additive, continuous-output, learned, or stateful models fall outside the workflow's primary scope. Applying only a subset of diagnostics can be reasonable, but label the result as a partial exploratory analysis.
