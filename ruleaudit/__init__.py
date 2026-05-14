"""
ruleaudit — a data-free structural audit protocol for expert-derived clinical decision rules.

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

__version__ = "0.1.0"
__all__ = [
    "RuleAudit", "InputSpec", "InputVar",
    "AuditResult", "FiringResult", "CorrelationResult",
    "VIFResult", "SensitivityResult", "IdentifiabilityResult", "MDLResult",
    "DEFAULT_THRESHOLDS", "render_report",
]
