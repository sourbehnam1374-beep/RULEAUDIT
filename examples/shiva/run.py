"""SHIVA SPIN-THA audit using the rules/ subpackage layout.

The rule, input spec and seeds live in `ruleaudit.rules.shiva_spintha` so the
audit reference has a single source of truth; this script just runs it (mirrors
the gap/ and lewinnek/ examples).
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from ruleaudit import RuleAudit, render_report
from ruleaudit.rules import shiva_spintha as shiva

audit = RuleAudit(
    rule=shiva.rule,
    input_spec=shiva.spec,
    driver_names=shiva.metadata["driver_names"],
)

if __name__ == "__main__":
    print(f"Running audit of {shiva.metadata['name']}...")
    result = audit.run(n_random=10000, seeds=shiva.seeds, n_saltelli=512)
    out = pathlib.Path(__file__).parent / "out"
    rpath = render_report(result, out, title=f"{shiva.metadata['name']} — RuleAudit Report")
    n_flags = sum(len(getattr(result, t).flags) for t in
                  ["firing", "correlation", "vif", "sensitivity", "identifiability"])
    print(f"  Report -> {rpath}")
    print(f"  Flags raised: {n_flags}")
