"""GAP audit using the new rules/ subpackage layout."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from ruleaudit import RuleAudit, render_report
from ruleaudit.rules import gap
from ruleaudit.samplers import asd_realistic

audit = RuleAudit(
    rule=gap.rule,
    input_spec=gap.spec,
    driver_names=gap.metadata["driver_names"],
)
audit.input_spec.joint_sampler = asd_realistic

if __name__ == "__main__":
    print(f"Running audit of {gap.metadata['name']}...")
    result = audit.run(n_random=10000, seeds=gap.seeds, n_saltelli=512)
    out = pathlib.Path(__file__).parent / "out"
    rpath = render_report(result, out, title=f"{gap.metadata['name']} — RuleAudit Report")
    n_flags = sum(len(getattr(result, t).flags) for t in
                  ["firing", "correlation", "vif", "sensitivity", "identifiability"])
    print(f"  Report → {rpath}")
    print(f"  Flags raised: {n_flags}")
