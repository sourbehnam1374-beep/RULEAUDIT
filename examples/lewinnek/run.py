"""Lewinnek audit using the rules/ subpackage layout."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from ruleaudit import RuleAudit, render_report
from ruleaudit.rules import lewinnek
from ruleaudit.samplers import tha_realistic


audit = RuleAudit(
    rule=lewinnek.rule,
    input_spec=lewinnek.spec,
    driver_names=lewinnek.metadata["driver_names"],
)
audit.input_spec.joint_sampler = tha_realistic


if __name__ == "__main__":
    print(f"Running audit of {lewinnek.metadata['name']}...")
    result = audit.run(n_random=10000, seeds=lewinnek.seeds, n_saltelli=1024)
    out = pathlib.Path(__file__).parent / "out"
    rpath = render_report(result, out, title=f"{lewinnek.metadata['name']} — RuleAudit Report")
    n_flags = sum(len(getattr(result, t).flags) for t in
                  ["firing", "correlation", "vif", "sensitivity", "identifiability"])
    print(f"  Report -> {rpath}")
    print(f"  Flags raised: {n_flags}")
