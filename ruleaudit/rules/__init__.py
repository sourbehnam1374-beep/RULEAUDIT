"""
ruleaudit.rules — a library of audited clinical decision rules.

Each rule module exposes:
  - a `rule(inp: dict) -> dict` callable (the rule itself)
  - a `spec` InputSpec describing inputs and ranges
  - a `seeds` dict of named reference cases for OAT analysis
  - a `metadata` dict describing the rule's provenance and clinical context

To add a new rule, copy `_template.py` and fill it in. The rule then becomes
auditable via `audit = build_audit_for(my_rule_module)`.
"""

from . import gap, lewinnek, shiva_spintha

__all__ = ["gap", "lewinnek", "shiva_spintha"]
