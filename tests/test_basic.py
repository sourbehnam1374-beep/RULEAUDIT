"""Basic tests for ruleaudit core."""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from importlib.metadata import version
from ruleaudit import RuleAudit, InputSpec, InputVar
import ruleaudit


def trivial_rule(inp):
    """Two-driver rule: high if value > 50, low if < 20."""
    drivers = {
        "high": 1 if inp["x"] > 50 else 0,
        "low":  1 if inp["x"] < 20 else 0,
    }
    return {"drivers": drivers, "total": sum(drivers.values())}


SPEC = InputSpec(vars=[InputVar("x", 0, 100)])


def test_basic_sweep():
    audit = RuleAudit(rule=trivial_rule, input_spec=SPEC, seed=1)
    sweep = audit.random_sweep(n=1000)
    assert len(sweep) == 1000
    assert "d_high" in sweep.columns and "d_low" in sweep.columns
    assert "total" in sweep.columns
    # Approximately uniform sampling: ~50% should fire 'high', ~20% should fire 'low'
    assert 0.40 < (sweep["d_high"] > 0).mean() < 0.60
    assert 0.15 < (sweep["d_low"] > 0).mean() < 0.25


def test_firing_flags():
    """A rule with an always-on driver should be flagged."""
    def always_on(inp):
        return {"drivers": {"always": 1, "rare": 1 if inp["x"] > 999 else 0},
                "total": 1 + (1 if inp["x"] > 999 else 0)}
    audit = RuleAudit(rule=always_on, input_spec=SPEC, seed=2)
    sweep = audit.random_sweep(n=1000)
    f = audit.test_firing(sweep)
    flag_text = " ".join(f.flags)
    assert "ALWAYS-ON" in flag_text or "DEAD" in flag_text


def test_correlation_perfect():
    """Two identical-condition drivers should be flagged r=1.0."""
    def two_twins(inp):
        a = 1 if inp["x"] > 50 else 0
        return {"drivers": {"d1": a, "d2": a}, "total": 2 * a}
    audit = RuleAudit(rule=two_twins, input_spec=SPEC, seed=3)
    sweep = audit.random_sweep(n=1000)
    c = audit.test_correlation(sweep)
    flag_text = " ".join(c.flags)
    assert "EXTREME-COLLINEAR" in flag_text


def test_run_end_to_end():
    """The .run() method should execute without error and return a populated result."""
    audit = RuleAudit(rule=trivial_rule, input_spec=SPEC, seed=4)
    seeds = {"mid": {"x": 50.0}}
    result = audit.run(n_random=500, seeds=seeds, n_saltelli=64)
    assert result.n_random == 500
    assert result.driver_names == ["high", "low"]
    assert len(result.firing.rates) == 2
    assert result.sensitivity.sobol_ST.sum() > 0


def test_runtime_version_matches_distribution_metadata():
    assert ruleaudit.__version__ == version("ruleaudit")


def test_sobol_results_are_reproducible_for_same_seed():
    seeds = {"mid": {"x": 50.0}}
    first = RuleAudit(rule=trivial_rule, input_spec=SPEC, seed=17)
    second = RuleAudit(rule=trivial_rule, input_spec=SPEC, seed=17)
    a = first.run(n_random=250, seeds=seeds, n_saltelli=64).sensitivity
    b = second.run(n_random=250, seeds=seeds, n_saltelli=64).sensitivity
    np.testing.assert_allclose(a.sobol_S1, b.sobol_S1, equal_nan=True)
    np.testing.assert_allclose(a.sobol_ST, b.sobol_ST, equal_nan=True)
    np.testing.assert_allclose(a.sobol_S1_conf, b.sobol_S1_conf, equal_nan=True)
    np.testing.assert_allclose(a.sobol_ST_conf, b.sobol_ST_conf, equal_nan=True)


if __name__ == "__main__":
    test_basic_sweep()
    print("PASS test_basic_sweep")
    test_firing_flags()
    print("PASS test_firing_flags")
    test_correlation_perfect()
    print("PASS test_correlation_perfect")
    test_run_end_to_end()
    print("PASS test_run_end_to_end")
    print("All tests passed.")
