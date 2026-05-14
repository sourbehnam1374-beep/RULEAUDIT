"""
ruleaudit.core — main audit class.

A RuleAudit binds together:
  - a deterministic rule (a Python callable taking a dict of inputs)
  - an InputSpec describing the inputs (ranges, distributions)
  - optional driver names and total-score extractor

The audit object generates synthetic samples and exposes the six tests
(firing_rates, correlation, vif, sensitivity, identifiability, mdl_debt)
plus a top-level .run() that executes all and returns an AuditResult.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple, Any
import numpy as np
import pandas as pd


# ============================================================
# Input spec
# ============================================================

@dataclass
class InputVar:
    """A single rule input."""
    name: str
    low: float
    high: float
    # Optional sampling distribution; 'uniform' or a callable returning a sample
    dist: str = "uniform"
    # For correlated samplers: a function of an rng + state dict can be set here
    sample_fn: Optional[Callable] = None


@dataclass
class InputSpec:
    """Collection of InputVars + optional joint sampler.

    If joint_sampler is given, it overrides per-variable sampling. It receives
    a numpy.random.Generator and returns a dict {name: value}. Use this when
    inputs are correlated (e.g., SS depends on PI).
    """
    vars: List[InputVar]
    joint_sampler: Optional[Callable[[np.random.Generator], Dict[str, float]]] = None

    @property
    def names(self) -> List[str]:
        return [v.name for v in self.vars]

    @property
    def bounds(self) -> List[Tuple[float, float]]:
        return [(v.low, v.high) for v in self.vars]


# ============================================================
# Result containers
# ============================================================

@dataclass
class FiringResult:
    rates: pd.Series
    mean_contribution: pd.Series
    flags: List[str] = field(default_factory=list)


@dataclass
class CorrelationResult:
    pearson: pd.DataFrame
    spearman: pd.DataFrame
    strong_pairs: pd.Series
    flags: List[str] = field(default_factory=list)


@dataclass
class VIFResult:
    vif: pd.Series
    flags: List[str] = field(default_factory=list)


@dataclass
class SensitivityResult:
    sobol_S1: pd.Series
    sobol_ST: pd.Series
    sobol_S1_conf: pd.Series
    sobol_ST_conf: pd.Series
    oat: pd.DataFrame
    flags: List[str] = field(default_factory=list)


@dataclass
class IdentifiabilityResult:
    per_total: pd.DataFrame  # columns: total, n_cases, n_patterns, diversity_ratio
    flags: List[str] = field(default_factory=list)


@dataclass
class MDLResult:
    L_M_expert: float
    L_DM_expert: float
    L_M_baseline: float
    L_DM_baseline: float
    debt_bits: float
    baseline_C: float
    baseline_nnz: int


@dataclass
class AuditResult:
    sweep: pd.DataFrame  # the random sweep
    firing: FiringResult
    correlation: CorrelationResult
    vif: VIFResult
    sensitivity: SensitivityResult
    identifiability: IdentifiabilityResult
    mdl: Optional[MDLResult] = None
    driver_names: List[str] = field(default_factory=list)
    n_random: int = 0


# ============================================================
# Audit class
# ============================================================

DEFAULT_THRESHOLDS = {
    "fire_dead":         0.000,   # exactly 0 → flag
    "fire_rare":         0.01,    # <1% → flag
    "fire_always_on":    0.90,    # >90% → flag
    "corr_strong":       0.50,
    "corr_extreme":      0.95,
    "vif_concern":       5.0,
    "vif_extreme":       100.0,
    "sobol_interaction": 0.50,    # (ST - S1)/ST > 0.5 → interaction-dominated
}


class RuleAudit:
    """Top-level audit object.

    Parameters
    ----------
    rule : callable
        Takes a dict of inputs, returns either:
          - a dict with keys 'drivers' (dict of name->contribution),
            'total' (number), and optionally 'category' (str)
          - or a tuple (drivers_dict, total)
    input_spec : InputSpec
    driver_names : list[str], optional
        If not given, inferred from the first rule call.
    thresholds : dict, optional
        Override DEFAULT_THRESHOLDS.
    """

    def __init__(self,
                 rule: Callable,
                 input_spec: InputSpec,
                 driver_names: Optional[Sequence[str]] = None,
                 thresholds: Optional[dict] = None,
                 seed: int = 42):
        self.rule = rule
        self.input_spec = input_spec
        self.thresholds = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        # Lazy: discover driver names from a probe call if not given
        self._driver_names: Optional[List[str]] = (
            list(driver_names) if driver_names is not None else None
        )

    # ------------------------------------------------------------
    # Rule invocation
    # ------------------------------------------------------------
    def _call(self, inputs: Dict[str, float]) -> Dict[str, Any]:
        out = self.rule(inputs)
        if isinstance(out, tuple) and len(out) == 2:
            drivers, total = out
            return {"drivers": drivers, "total": total}
        if not isinstance(out, dict):
            raise TypeError("Rule must return dict or (drivers, total)")
        if "drivers" not in out or "total" not in out:
            raise ValueError("Rule output must contain 'drivers' and 'total'")
        return out

    def _ensure_driver_names(self, sample_inputs: Dict[str, float]):
        if self._driver_names is None:
            r = self._call(sample_inputs)
            self._driver_names = list(r["drivers"].keys())

    # ------------------------------------------------------------
    # Sampling
    # ------------------------------------------------------------
    def _sample_one(self) -> Dict[str, float]:
        if self.input_spec.joint_sampler is not None:
            return self.input_spec.joint_sampler(self.rng)
        out = {}
        for v in self.input_spec.vars:
            if v.sample_fn is not None:
                out[v.name] = v.sample_fn(self.rng)
            else:
                out[v.name] = float(self.rng.uniform(v.low, v.high))
        return out

    def random_sweep(self, n: int = 10000) -> pd.DataFrame:
        rows = []
        first = self._sample_one()
        self._ensure_driver_names(first)
        r0 = self._call(first)
        row0 = {**first, "total": r0["total"],
                **{f"d_{k}": v for k, v in r0["drivers"].items()}}
        if "category" in r0:
            row0["category"] = r0["category"]
        rows.append(row0)
        for _ in range(n - 1):
            inp = self._sample_one()
            r = self._call(inp)
            row = {**inp, "total": r["total"],
                   **{f"d_{k}": v for k, v in r["drivers"].items()}}
            if "category" in r:
                row["category"] = r["category"]
            rows.append(row)
        return pd.DataFrame(rows)

    def oat_sweep(self,
                  seeds: Dict[str, Dict[str, float]],
                  steps: int = 50) -> pd.DataFrame:
        """One-at-a-time sweep around each seed."""
        rows = []
        for seed_name, seed_inputs in seeds.items():
            for var in self.input_spec.vars:
                lo, hi = var.low, var.high
                values = np.linspace(lo, hi, steps)
                for v in values:
                    inp = {**seed_inputs, var.name: float(v)}
                    r = self._call(inp)
                    rows.append({
                        "seed": seed_name, "swept_param": var.name,
                        "swept_value": v, "total": r["total"],
                        "category": r.get("category"),
                    })
        return pd.DataFrame(rows)

    # ------------------------------------------------------------
    # Six tests
    # ------------------------------------------------------------
    def test_firing(self, sweep: pd.DataFrame) -> FiringResult:
        cols = [f"d_{n}" for n in self._driver_names]
        rates = (sweep[cols] > 0).mean()
        rates.index = self._driver_names
        contrib = sweep[cols].mean()
        contrib.index = self._driver_names

        flags = []
        for name in self._driver_names:
            r = rates[name]
            if r <= self.thresholds["fire_dead"]:
                flags.append(f"DEAD: '{name}' fires in 0 of {len(sweep)} cases")
            elif r < self.thresholds["fire_rare"]:
                flags.append(f"RARE: '{name}' fires in {100*r:.2f}% of cases")
            if r > self.thresholds["fire_always_on"]:
                flags.append(f"ALWAYS-ON: '{name}' fires in {100*r:.1f}% of cases")
        return FiringResult(rates=rates, mean_contribution=contrib, flags=flags)

    def test_correlation(self, sweep: pd.DataFrame) -> CorrelationResult:
        cols = [f"d_{n}" for n in self._driver_names]
        A = sweep[cols].copy()
        A.columns = self._driver_names
        # drop zero-variance
        A = A.loc[:, A.std() > 0]
        pearson = A.corr(method="pearson")
        spearman = A.corr(method="spearman")

        upper = pearson.where(np.triu(np.ones_like(pearson, dtype=bool), k=1))
        pairs = upper.stack().abs().sort_values(ascending=False)
        strong = pairs[pairs > self.thresholds["corr_strong"]]

        flags = []
        for (a, b), r in strong.items():
            if r >= self.thresholds["corr_extreme"]:
                flags.append(f"EXTREME-COLLINEAR: '{a}' ↔ '{b}' (|r|={r:.3f})")
            else:
                flags.append(f"COLLINEAR: '{a}' ↔ '{b}' (|r|={r:.3f})")
        return CorrelationResult(pearson=pearson, spearman=spearman,
                                 strong_pairs=strong, flags=flags)

    def test_vif(self, sweep: pd.DataFrame) -> VIFResult:
        from statsmodels.stats.outliers_influence import variance_inflation_factor
        from statsmodels.tools.tools import add_constant

        cols = [f"d_{n}" for n in self._driver_names]
        A = sweep[cols].copy()
        A.columns = self._driver_names
        A = A.loc[:, A.std() > 0]

        X = add_constant(A.values)
        vif = pd.Series(
            [variance_inflation_factor(X, i + 1) for i in range(A.shape[1])],
            index=A.columns,
        ).sort_values(ascending=False)

        flags = []
        for name, v in vif.items():
            if np.isinf(v) or v > self.thresholds["vif_extreme"]:
                flags.append(f"EXTREME-VIF: '{name}' has VIF={v:.2e}")
            elif v > self.thresholds["vif_concern"]:
                flags.append(f"HIGH-VIF: '{name}' has VIF={v:.2f}")
        return VIFResult(vif=vif, flags=flags)

    def test_sensitivity(self,
                         seeds: Dict[str, Dict[str, float]],
                         n_saltelli: int = 1024,
                         oat_steps: int = 50) -> SensitivityResult:
        from SALib.sample import sobol as sobol_sample
        from SALib.analyze import sobol as sobol_analyze

        problem = {
            "num_vars": len(self.input_spec.vars),
            "names":    self.input_spec.names,
            "bounds":   [list(b) for b in self.input_spec.bounds],
        }
        X = sobol_sample.sample(problem, n_saltelli, calc_second_order=False)
        Y = np.empty(len(X))
        for i, row in enumerate(X):
            inp = dict(zip(problem["names"], row))
            Y[i] = self._call(inp)["total"]
        Si = sobol_analyze.analyze(problem, Y, calc_second_order=False,
                                   print_to_console=False)
        names = problem["names"]
        S1 = pd.Series(Si["S1"], index=names)
        ST = pd.Series(Si["ST"], index=names)
        S1c = pd.Series(Si["S1_conf"], index=names)
        STc = pd.Series(Si["ST_conf"], index=names)

        oat = self.oat_sweep(seeds, steps=oat_steps)

        flags = []
        for n in names:
            if ST[n] > 0:
                interaction_share = max(0, (ST[n] - S1[n]) / ST[n])
                if interaction_share > self.thresholds["sobol_interaction"] and ST[n] > 0.05:
                    flags.append(
                        f"INTERACTION-DOMINATED: '{n}' "
                        f"(S1={S1[n]:.3f}, ST={ST[n]:.3f}, interaction share {interaction_share:.1%})"
                    )
            # Detect inert inputs: ST near zero
            if ST[n] < 0.005:
                flags.append(f"INERT: '{n}' has ST={ST[n]:.4f} — input does not move score")

        return SensitivityResult(sobol_S1=S1, sobol_ST=ST, sobol_S1_conf=S1c,
                                 sobol_ST_conf=STc, oat=oat, flags=flags)

    def test_identifiability(self, sweep: pd.DataFrame) -> IdentifiabilityResult:
        cols = [f"d_{n}" for n in self._driver_names]
        patterns = sweep[cols].apply(lambda r: tuple(int(x) for x in r), axis=1)
        df = pd.DataFrame({"total": sweep["total"], "pattern": patterns})

        rows = []
        for total, g in df.groupby("total"):
            if len(g) < 5:
                continue
            rows.append({
                "total": int(total), "n_cases": len(g),
                "n_patterns": g["pattern"].nunique(),
                "diversity_ratio": g["pattern"].nunique() / len(g),
            })
        per_total = pd.DataFrame(rows).sort_values("total")

        flags = []
        # Look for high collapse near band boundaries: low diversity, high N
        for _, r in per_total.iterrows():
            if r["n_cases"] >= 100 and r["diversity_ratio"] < 0.02:
                flags.append(
                    f"COLLAPSE: total={r['total']} has {r['n_cases']} cases collapsing "
                    f"to {r['n_patterns']} patterns (div={r['diversity_ratio']:.3f})"
                )
        # And the opposite: high diversity at clinically critical mid-range
        mid = per_total[(per_total["diversity_ratio"] > 0.025) &
                       (per_total["n_cases"] >= 200)]
        for _, r in mid.iterrows():
            flags.append(
                f"MECH-SPRAWL: total={r['total']} encodes {r['n_patterns']} distinct "
                f"mechanism patterns across {r['n_cases']} cases"
            )
        return IdentifiabilityResult(per_total=per_total, flags=flags)

    def test_mdl(self,
                 sweep: pd.DataFrame,
                 y: np.ndarray,
                 raw_input_cols: List[str],
                 L_M_expert: int) -> MDLResult:
        """MDL calibration debt vs L1-logistic baseline.

        y          : binary outcome (1D ndarray of 0/1, length matching sweep)
        raw_inputs : list of column names in sweep representing the raw inputs
                     (not the driver activations)
        L_M_expert : caller-supplied estimate of expert rule encoding length in bits.
        """
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler
        from sklearn.metrics import log_loss

        X_raw = sweep[raw_input_cols].values
        X_std = StandardScaler().fit_transform(X_raw)
        n = len(y)

        # Conditional entropy of y given the rule's total (in bits)
        H = 0.0
        df_h = pd.DataFrame({"y": y, "x": sweep["total"].values})
        for _, g in df_h.groupby("x"):
            p = g["y"].mean()
            if 0 < p < 1:
                h_x = -(p * np.log2(p) + (1 - p) * np.log2(1 - p))
            else:
                h_x = 0
            H += (len(g) / n) * h_x
        L_DM_expert = n * H

        # L1-logistic baseline over a grid of C
        best = None
        for C in [0.01, 0.03, 0.1, 0.3, 1.0, 3.0]:
            m = LogisticRegression(penalty="l1", solver="liblinear",
                                   C=C, max_iter=2000).fit(X_std, y)
            nnz = int((np.abs(m.coef_) > 1e-6).sum())
            L_M_b = nnz * 32 + 32
            p = m.predict_proba(X_std)[:, 1]
            p = np.clip(p, 1e-6, 1 - 1e-6)
            L_DM_b = n * log_loss(y, p) / np.log(2)
            total = L_M_b + L_DM_b
            if best is None or total < best["total"]:
                best = dict(C=C, nnz=nnz, L_M=L_M_b, L_DM=L_DM_b, total=total)

        debt = (L_M_expert + L_DM_expert) - best["total"]
        return MDLResult(
            L_M_expert=L_M_expert, L_DM_expert=L_DM_expert,
            L_M_baseline=best["L_M"], L_DM_baseline=best["L_DM"],
            debt_bits=debt, baseline_C=best["C"], baseline_nnz=best["nnz"],
        )

    # ------------------------------------------------------------
    # Top-level run
    # ------------------------------------------------------------
    def run(self,
            n_random: int = 10000,
            seeds: Optional[Dict[str, Dict[str, float]]] = None,
            n_saltelli: int = 1024,
            mdl_inputs: Optional[Tuple[np.ndarray, List[str], int]] = None,
            ) -> AuditResult:
        """Execute all six tests in order."""
        # Random sweep
        sweep = self.random_sweep(n_random)
        # Tests
        firing = self.test_firing(sweep)
        corr   = self.test_correlation(sweep)
        vif    = self.test_vif(sweep)
        if seeds is None:
            # Build a single seed at the midpoint of every input
            seeds = {"mid": {v.name: 0.5 * (v.low + v.high) for v in self.input_spec.vars}}
        sens   = self.test_sensitivity(seeds, n_saltelli=n_saltelli)
        ident  = self.test_identifiability(sweep)
        mdl    = None
        if mdl_inputs is not None:
            y, raw_cols, L_M = mdl_inputs
            mdl = self.test_mdl(sweep, y, raw_cols, L_M)
        return AuditResult(
            sweep=sweep, firing=firing, correlation=corr, vif=vif,
            sensitivity=sens, identifiability=ident, mdl=mdl,
            driver_names=self._driver_names or [], n_random=n_random,
        )
