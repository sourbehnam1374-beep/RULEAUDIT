"""
ruleaudit.reporting — render audit results to markdown + figures.
"""

from __future__ import annotations
import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
from typing import Optional

from .core import AuditResult


def _setup_mpl():
    mpl.rcParams.update({
        "font.size": 9, "axes.labelsize": 10, "axes.titlesize": 11,
        "figure.dpi": 130, "savefig.dpi": 200, "savefig.bbox": "tight",
        "axes.spines.top": False, "axes.spines.right": False,
    })


def plot_correlation(result: AuditResult, out: Path):
    _setup_mpl()
    pearson = result.correlation.pearson
    labels = list(pearson.columns)
    fig, ax = plt.subplots(figsize=(max(4.5, 0.5 * len(labels) + 1.5),
                                    max(4.5, 0.5 * len(labels) + 1.5)))
    im = ax.imshow(pearson.values, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(labels))); ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels)
    for i in range(len(labels)):
        for j in range(len(labels)):
            v = pearson.values[i, j]
            if abs(v) > 0.3 and i != j:
                ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                        color="white" if abs(v) > 0.6 else "black", fontsize=7.5)
    fig.colorbar(im, ax=ax, shrink=0.7).set_label("Pearson r")
    ax.set_title("Driver activation correlation")
    plt.savefig(out); plt.close()


def plot_vif(result: AuditResult, out: Path):
    _setup_mpl()
    vif = result.vif.vif.copy().replace([np.inf, -np.inf], 1e10).sort_values()
    fig, ax = plt.subplots(figsize=(6, max(3, 0.35 * len(vif))))
    colors = ["#d62728" if v > 5 else "#7f7f7f" if v > 2 else "#2ca02c" for v in vif]
    ax.barh(range(len(vif)), vif.values, color=colors, edgecolor="black", linewidth=0.4)
    if vif.max() > 100:
        ax.set_xscale("log")
    ax.set_yticks(range(len(vif))); ax.set_yticklabels(vif.index)
    ax.axvline(5, color="black", linestyle="--", linewidth=0.7, alpha=0.5)
    ax.axvline(2, color="black", linestyle=":", linewidth=0.7, alpha=0.5)
    ax.set_xlabel("Variance Inflation Factor")
    ax.set_title("VIF per driver")
    plt.savefig(out); plt.close()


def plot_sensitivity_sobol(result: AuditResult, out: Path):
    _setup_mpl()
    S1 = result.sensitivity.sobol_S1
    ST = result.sensitivity.sobol_ST
    S1c = result.sensitivity.sobol_S1_conf
    STc = result.sensitivity.sobol_ST_conf
    order = ST.sort_values().index.tolist()
    S1, ST = S1.loc[order], ST.loc[order]
    S1c, STc = S1c.loc[order], STc.loc[order]

    fig, ax = plt.subplots(figsize=(7, max(3, 0.45 * len(order))))
    xs = np.arange(len(order)); width = 0.36
    ax.barh(xs - width / 2, S1.values, width, label="S1 (first-order)",
            color="#1f77b4", edgecolor="black", linewidth=0.4,
            xerr=S1c.values, error_kw={"linewidth": 0.6, "ecolor": "gray"})
    ax.barh(xs + width / 2, ST.values, width, label="ST (total-order)",
            color="#d62728", edgecolor="black", linewidth=0.4,
            xerr=STc.values, error_kw={"linewidth": 0.6, "ecolor": "gray"})
    ax.set_yticks(xs); ax.set_yticklabels(order)
    ax.set_xlabel("Sobol index")
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    ax.set_title("Sobol sensitivity indices")
    plt.savefig(out); plt.close()


def plot_identifiability(result: AuditResult, out: Path):
    _setup_mpl()
    div = result.identifiability.per_total
    if len(div) == 0:
        return
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.scatter(div["total"], div["diversity_ratio"],
               s=np.clip(div["n_cases"], 5, 200), alpha=0.7,
               color="#1f77b4", edgecolor="black", linewidth=0.3)
    ax.set_xlabel("Total score")
    ax.set_ylabel("Diversity ratio (distinct patterns / cases)")
    ax.set_title("Mechanism identifiability per total score")
    plt.savefig(out); plt.close()


def plot_oat(result: AuditResult, out: Path):
    _setup_mpl()
    oat = result.sensitivity.oat
    if oat is None or len(oat) == 0:
        return
    params = sorted(oat["swept_param"].unique())
    seeds_in_data = sorted(oat["seed"].unique())
    cols = 3
    rows = (len(params) + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(4.0 * cols, 3.0 * rows), sharey=True)
    palette = ["#1f77b4", "#d62728", "#2ca02c", "#ff7f0e", "#9467bd"]
    flat = axes.flat if hasattr(axes, "flat") else [axes]
    for ax, p in zip(flat, params):
        for i, s in enumerate(seeds_in_data):
            sub = oat[(oat["seed"] == s) & (oat["swept_param"] == p)].sort_values("swept_value")
            ax.plot(sub["swept_value"], sub["total"],
                    color=palette[i % len(palette)], linewidth=1.4, label=s)
        ax.set_title(p, fontsize=9)
        ax.tick_params(labelsize=8)
    for ax in flat[len(params):]:
        ax.axis("off")
    flat[0].legend(fontsize=8, frameon=False)
    fig.suptitle("One-at-a-time sensitivity per seed", x=0.01, ha="left")
    plt.tight_layout()
    plt.savefig(out); plt.close()


# ============================================================
# Markdown report
# ============================================================

def render_report(result: AuditResult, outdir: Path, title: str = "RuleAudit Report") -> Path:
    """Write a markdown report + figures into outdir/. Returns the report path."""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # Figures
    plot_correlation(result, outdir / "fig_correlation.png")
    plot_vif(result, outdir / "fig_vif.png")
    plot_sensitivity_sobol(result, outdir / "fig_sobol.png")
    plot_identifiability(result, outdir / "fig_identifiability.png")
    plot_oat(result, outdir / "fig_oat.png")

    # Tabular CSVs
    result.sweep.to_csv(outdir / "sweep_random.csv", index=False)
    result.correlation.pearson.to_csv(outdir / "pearson.csv")
    result.vif.vif.to_csv(outdir / "vif.csv", header=["VIF"])
    pd.DataFrame({
        "fire_rate": result.firing.rates,
        "mean_contrib": result.firing.mean_contribution,
    }).to_csv(outdir / "firing.csv")
    pd.DataFrame({
        "S1": result.sensitivity.sobol_S1,
        "ST": result.sensitivity.sobol_ST,
        "S1_conf": result.sensitivity.sobol_S1_conf,
        "ST_conf": result.sensitivity.sobol_ST_conf,
    }).to_csv(outdir / "sobol.csv")
    result.identifiability.per_total.to_csv(outdir / "identifiability.csv", index=False)
    result.sensitivity.oat.to_csv(outdir / "oat.csv", index=False)

    # Build markdown
    lines = [f"# {title}\n",
             f"**N synthetic cases:** {result.n_random:,}",
             f"**Drivers analysed:** {len(result.driver_names)}\n"]

    # Summary flags
    all_flags = []
    all_flags += [("Firing", f) for f in result.firing.flags]
    all_flags += [("Correlation", f) for f in result.correlation.flags]
    all_flags += [("VIF", f) for f in result.vif.flags]
    all_flags += [("Sensitivity", f) for f in result.sensitivity.flags]
    all_flags += [("Identifiability", f) for f in result.identifiability.flags]

    lines.append("## Headline diagnostics\n")
    if not all_flags:
        lines.append("_No structural flags raised._\n")
    else:
        for area, flag in all_flags:
            lines.append(f"- **{area}**: {flag}")
        lines.append("")

    # Firing
    lines.append("## 1. Driver firing rates\n")
    df = pd.DataFrame({
        "fire_rate": result.firing.rates.round(3),
        "mean_contrib": result.firing.mean_contribution.round(2),
    }).sort_values("fire_rate", ascending=False)
    lines.append(df.to_markdown())
    lines.append("")

    # Correlation
    lines.append("## 2. Driver orthogonality\n")
    lines.append(f"Maximum off-diagonal |r| = "
                 f"{result.correlation.strong_pairs.iloc[0] if len(result.correlation.strong_pairs) > 0 else 0:.3f}\n")
    lines.append("![Correlation heatmap](fig_correlation.png)\n")

    # VIF
    lines.append("## 3. Variance Inflation Factor\n")
    lines.append(result.vif.vif.round(3).to_frame("VIF").to_markdown())
    lines.append("\n![VIF](fig_vif.png)\n")

    # Sensitivity
    lines.append("## 4. Sensitivity analysis\n")
    sob = pd.DataFrame({
        "S1": result.sensitivity.sobol_S1.round(3),
        "ST": result.sensitivity.sobol_ST.round(3),
    }).sort_values("ST", ascending=False)
    lines.append(sob.to_markdown())
    lines.append("\n![Sobol indices](fig_sobol.png)\n")
    lines.append("![OAT sensitivity](fig_oat.png)\n")

    # Identifiability
    lines.append("## 5. Identifiability per total score\n")
    if len(result.identifiability.per_total) > 0:
        lines.append(result.identifiability.per_total.to_markdown(index=False))
    lines.append("\n![Identifiability](fig_identifiability.png)\n")

    # MDL
    if result.mdl is not None:
        lines.append("## 6. MDL calibration debt\n")
        m = result.mdl
        lines.append(f"- Expert rule: L(M)={m.L_M_expert:.0f}, L(D|M)={m.L_DM_expert:.0f}, Total={m.L_M_expert + m.L_DM_expert:.0f} bits")
        lines.append(f"- L1 baseline (C={m.baseline_C}, k={m.baseline_nnz}): L(M)={m.L_M_baseline:.0f}, L(D|M)={m.L_DM_baseline:.0f}, Total={m.L_M_baseline + m.L_DM_baseline:.0f} bits")
        lines.append(f"- **Calibration debt = {m.debt_bits:+.0f} bits** "
                     f"({'expert rule less efficient' if m.debt_bits > 0 else 'expert rule more efficient'})")
        lines.append("")

    rpath = outdir / "report.md"
    rpath.write_text("\n".join(lines))
    return rpath
