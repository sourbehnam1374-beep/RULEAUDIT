"""
ruleaudit — outcome-free structural screening for deterministic additive clinical scores.

Usage:
    from ruleaudit import RuleAudit, InputSpec, InputVar
    audit = RuleAudit(rule=my_rule, input_spec=spec)
    result = audit.run(n_random=10000)
    from ruleaudit.reporting import render_report
    render_report(result, "out/")
"""

from .core import (
    RuleAudit,
    InputSpec,
    InputVar,
    AuditResult,
    FiringResult,
    CorrelationResult,
    VIFResult,
    SensitivityResult,
    IdentifiabilityResult,
    MDLResult,
    DEFAULT_THRESHOLDS,
)
from .reporting import render_report

# Single source of truth is pyproject.toml; read installed metadata when
# available so the string can't drift from the packaged version.
try:
    from importlib.metadata import version as _pkg_version
    __version__ = _pkg_version("ruleaudit")
except Exception:  # not installed (e.g. run from source tree)
    __version__ = "0.2.1"
__all__ = [
    "RuleAudit", "InputSpec", "InputVar",
    "AuditResult", "FiringResult", "CorrelationResult",
    "VIFResult", "SensitivityResult", "IdentifiabilityResult", "MDLResult",
    "DEFAULT_THRESHOLDS", "render_report",
]
