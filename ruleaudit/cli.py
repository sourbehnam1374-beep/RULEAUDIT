"""
ruleaudit CLI.

Usage:
    python -m ruleaudit.cli run <example_script.py> --out <dir>

The script must be a Python file that exposes either a module-level variable
`audit` of type RuleAudit, or a `build_audit()` function returning one. It may
optionally expose a `seeds` dict. The output directory is controlled by --out.
"""

import argparse
import importlib.util
import pathlib
import sys

from .core import RuleAudit
from .reporting import render_report


def _load_script(path: str):
    p = pathlib.Path(path).resolve()
    spec = importlib.util.spec_from_file_location("user_rule_script", p)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["user_rule_script"] = mod
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser(prog="ruleaudit",
                                 description="Structural audit for clinical decision rules.")
    sp = ap.add_subparsers(dest="cmd", required=True)

    run = sp.add_parser("run", help="Run a full audit from a user script.")
    run.add_argument("script", help="Path to Python file exposing `audit`.")
    run.add_argument("--out", default="ruleaudit_out",
                     help="Output directory (default: ruleaudit_out)")
    run.add_argument("--n-random", type=int, default=10000)
    run.add_argument("--n-saltelli", type=int, default=512)
    run.add_argument("--title", default="RuleAudit Report")

    args = ap.parse_args()

    if args.cmd == "run":
        mod = _load_script(args.script)
        if not hasattr(mod, "audit") or not isinstance(mod.audit, RuleAudit):
            # also accept a builder function
            if hasattr(mod, "build_audit"):
                mod.audit = mod.build_audit()
            else:
                raise SystemExit("Script must define module-level `audit: RuleAudit` "
                                 "or `build_audit()` returning one.")
        seeds = getattr(mod, "seeds", None)
        result = mod.audit.run(n_random=args.n_random, seeds=seeds,
                               n_saltelli=args.n_saltelli)
        rpath = render_report(result, args.out, title=args.title)
        print(f"Wrote report -> {rpath}")


if __name__ == "__main__":
    main()
