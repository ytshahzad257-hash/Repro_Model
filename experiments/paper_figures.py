"""Publication figures (vector PDF) generated only from results/generated/*.json.

Figure 5(b): Theorem 1 private-evidence width per question class, K = 1..3.
Figure 8:    distinct states of single-copy models and self-composition products.
Figure 9:    conservative quarantine versus true dependence (Section 7.5).
Usage: python experiments/paper_figures.py [output_dir]
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import os,tempfile
os.environ.setdefault("MPLCONFIGDIR",tempfile.mkdtemp(prefix="apr_matplotlib_"))
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "results" / "generated"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "figures" / "paper"

plt.rcParams.update({
    "text.usetex": False,
    "font.family": "serif",
    "font.serif": ["cmr10", "DejaVu Serif"],
    "mathtext.fontset": "cm",
    "axes.formatter.use_mathtext": True,
    "axes.unicode_minus": False,
    "font.size": 10,
    "axes.titlesize": 10,
    "axes.labelsize": 10,
    "legend.fontsize": 8.5,
    "xtick.labelsize": 10,
    "ytick.labelsize": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": "#DDDDDD",
    "grid.linewidth": 0.5,
    "pdf.fonttype": 42,
})

CONFIG_STYLE = {
    "Governed": ("#1F5A96", "o", "-"),
    "SourceOnly": ("#E07B00", "s", "-"),
    "IgnoreInfoChecks": ("#7B3FA0", "D", "-"),
    "UnguardedExport": ("#2E7D32", "^", "-"),
    "DeleteEvidence": ("#C62828", "v", "-"),
    "IgnoreGrantChecks": ("#6D4C41", "P", "--"),
    "TimedRelease": ("#D81B60", "X", ":"),
    "ApprovedSecretRelease": ("#00838F", "*", "--"),
    "RefusalMutation": ("#222222", "+", "-."),
}


def load(name: str) -> dict:
    return json.loads((GENERATED / name).read_text(encoding="utf-8"))


def fig5b() -> None:
    rows = load("question_class_bounds.json")["rows"]
    classes = [("admission_bits", "Admission"), ("enforcement_order_bits", "Enforcement\norder"),
               ("final_state_bits", "Final\nstate"), ("family_bits", "Combined\nfamily"),
               ("full_ex_post_bits", "Full history\n(ex post)")]
    colors = ["#CDDEEF", "#8CB2D9", "#4F86C6", "#1F3F73"]
    fig, ax = plt.subplots(figsize=(5.0, 2.8))
    width = 0.19
    for j, row in enumerate(rows):
        xs = [i + (j - (len(rows)-1)/2) * width for i in range(len(classes))]
        ys = [row[key] for key, _ in classes]
        bars = ax.bar(xs, ys, width, color=colors[j], label=f"$K={row['sources']}$", edgecolor="white", linewidth=0.4)
        for x, y in zip(xs, ys):
            ax.text(x, y + 0.25, str(y), ha="center", va="bottom", fontsize=8.2)
    ax.set_xticks(range(len(classes)))
    ax.set_xticklabels([label for _, label in classes])
    ax.set_ylabel("private bits")
    ax.set_ylim(0, max(r["full_ex_post_bits"] for r in rows) + 2.5)
    ax.grid(axis="x", visible=False)
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout(pad=0.3)
    fig.savefig(OUT / "fig5b_bits.pdf")
    plt.close(fig)


def fig8() -> None:
    rows = load("model_matrix.json")["rows"]
    fig, axes = plt.subplots(1, 2, figsize=(5.0, 3.3), sharey=True)
    for config, (color, marker, style) in CONFIG_STYLE.items():
        sel = sorted((r for r in rows if r["configuration"] == config and r.get("secrets","shared")=="shared"), key=lambda r: r["sources"])
        ks = [r["sources"] for r in sel]
        axes[0].plot(ks, [r["state_count_s0"] for r in sel], color=color, marker=marker, linestyle=style, linewidth=1, markersize=3.5, label=config)
        axes[1].plot(ks, [r["product_states"] for r in sel], color=color, marker=marker, linestyle=style, linewidth=1, markersize=3.5, label=config)
    for ax, title in zip(axes, ("(a) Single copy ($s=0$)", "(b) Self-composition product")):
        ax.set_yscale("log")
        ax.set_xticks(sorted({r["sources"] for r in rows}))
        ax.set_xlabel("restricted sources $K$")
        ax.set_title(title)
    axes[0].set_ylabel("distinct states")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, loc="lower center", ncol=3, fontsize=8.0)
    fig.tight_layout(pad=0.3, rect=(0, 0.28, 1, 1))
    fig.savefig(OUT / "fig8_scaling.pdf")
    plt.close(fig)


def fig9() -> None:
    doc = load("table7.json")
    rows, growth = doc["rows"], doc["growth_rows"]
    series = [("quarantined", "quarantined by conservative labels", "#1F5A96", "o"),
              ("truly_dependent", "truly dependent on revoked sources", "#C62828", "s"),
              ("withheld_clean", "withheld although clean", "#7F7F7F", "^")]
    fig, axes = plt.subplots(1, 2, figsize=(5.0, 3.3))
    for key, label, color, marker in series:
        axes[0].errorbar([r["use_probability"] for r in rows], [r[key] for r in rows], yerr=[r[f"{key}_half_width"] for r in rows],
                         color=color, marker=marker, markersize=3.5, linewidth=1, capsize=2, label=label)
        axes[1].errorbar([r["derived"] for r in growth], [r[key] for r in growth], yerr=[r[f"{key}_half_width"] for r in growth],
                         color=color, marker=marker, markersize=3.5, linewidth=1, capsize=2, label=label)
    axes[0].set_xlabel("use probability $u$")
    axes[0].set_title(f"(a) Input use ($n={doc['metadata']['inputs']['derived']}$)")
    axes[0].set_xticks([r["use_probability"] for r in rows])
    axes[1].set_xscale("log")
    axes[1].set_xticks([r["derived"] for r in growth])
    axes[1].get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    axes[1].minorticks_off()
    axes[1].set_xlabel("derived items per workflow $n$")
    axes[1].set_title("(b) Workflow length ($u=0.5$)")
    for ax in axes:
        ax.set_ylabel("share of derived items")
        ax.set_ylim(bottom=0)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, loc="lower center", ncol=2, fontsize=8.0)
    fig.tight_layout(pad=0.3, rect=(0, 0.15, 1, 1))
    fig.savefig(OUT / "fig9_quarantine.pdf")
    plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    fig5b()
    fig8()
    fig9()
    sys.path.insert(0,str(ROOT/"scripts"))
    from revision6_figures import build
    build(OUT)
    if (GENERATED/'agent/v6_3_revoked_cheapest_memory_only/summary.json').exists():
        from decision_figure_v6_3 import build as decision_figure
        decision_figure(OUT)
    print("wrote", OUT)
