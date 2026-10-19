"""Plot the quarantine-robustness and decision-experiment charts from saved result JSON.

Usage: python scripts/final_figures.py results/generated <output-dir>
"""
import json, sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

GEN = Path(sys.argv[1])          # artifact/results/generated
OUT = Path(sys.argv[2])          # output directory
plt.rcParams.update({
    "text.usetex": False, "font.family": "serif", "font.serif": ["cmr10", "DejaVu Serif"],
    "mathtext.fontset": "cm", "axes.formatter.use_mathtext": True, "axes.unicode_minus": False,
    "font.size": 9, "axes.titlesize": 9, "axes.labelsize": 9, "legend.fontsize": 8.5,
    "xtick.labelsize": 8.5, "ytick.labelsize": 8.5, "axes.spines.top": False, "axes.spines.right": False,
    "pdf.fonttype": 42,
})
BLUE, ORANGE, GREEN, GREY, RED = "#1F5A96", "#C77C0E", "#2E7D32", "#7A7A7A", "#B34B31"

def robustness():
    doc = json.loads((GEN / "robustness/summary.json").read_text())
    rows = [r for r in doc["rows"] if abs(r["restriction_probability"] - 0.1) < 1e-9 and r["derived"] == 100]
    sel_order = ["uniform", "recency", "zipf"]; use_order = ["independent", "correlated", "first_only"]
    use_lab = {"independent": "independent use", "correlated": "correlated use", "first_only": "first input only"}
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.05, 3.6), gridspec_kw={"width_ratios": [1.2, 1]})
    y, labels, k = [], [], 0
    for s in sel_order:
        for u in use_order:
            r = next(x for x in rows if x["selection"] == s and x["use_model"] == u)
            pos = k + sel_order.index(s) * 0.7
            a.barh(pos, r["truly_dependent"], color=BLUE, height=0.72)
            a.barh(pos, r["withheld_clean"], left=r["truly_dependent"], color="#AFC6E0", height=0.72)
            a.errorbar(r["quarantined"], pos, xerr=r["quarantined_half_width"], fmt="none", ecolor="black", capsize=2, lw=0.8)
            y.append(pos); labels.append(f"{s.capitalize()}, {use_lab[u]}"); k += 1
    a.set_yticks(y, labels); a.invert_yaxis(); a.set_xlim(0, 0.85)
    a.set_xlabel("share of derived items")
    a.set_title("(a) $n=100$, $p_r=0.1$", fontsize=10.5)
    a.grid(axis="x", color="#DDDDDD", lw=0.5); a.set_axisbelow(True)
    a.legend(handles=[Patch(color=BLUE, label="truly dependent"), Patch(color="#AFC6E0", label="withheld although clean")],
             loc="upper center", bbox_to_anchor=(0.45, -0.2), ncol=1, frameon=False)
    g = [r for r in doc["growth_rows"] if r["selection"] == "recency"]
    ns = sorted({r["derived"] for r in g})
    q = [next(r for r in g if r["derived"] == n and r["use_model"] == "independent") for n in ns]
    b.errorbar(ns, [r["quarantined"] for r in q], yerr=[r["quarantined_half_width"] for r in q], color="black", marker="o", ms=3.5, capsize=2, lw=1.2, label="quarantined (every use model)")
    for u, c, m in zip(use_order, (BLUE, ORANGE, GREEN), ("s", "^", "D")):
        rr = [next(r for r in g if r["derived"] == n and r["use_model"] == u) for n in ns]
        b.errorbar(ns, [r["truly_dependent"] for r in rr], yerr=[r["truly_dependent_half_width"] for r in rr], color=c, marker=m, ms=3.5, capsize=2, lw=1.0, ls="--", label=f"dependent, {use_lab[u]}")
    b.set_xscale("log", base=2); b.set_xticks(ns, [str(n) for n in ns]); b.minorticks_off()
    b.set_ylim(0, 1.0); b.set_xlabel("derived items $n$"); b.set_ylabel("share of derived items")
    b.set_title("(b) Recency, $p_r=0.1$", fontsize=10.5); b.grid(color="#DDDDDD", lw=0.5)
    b.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.45, -0.2), ncol=1)
    fig.tight_layout(pad=0.4, w_pad=1.0); fig.savefig(OUT / "quarantine_robustness.pdf"); plt.close(fig)

def decision():
    s = json.loads((GEN / "agent/v6_3_revoked_cheapest_memory_only/summary.json").read_text())
    assert s["complete"] and s["arm"] == "memory_only" and s["tasks"] == 100
    rows = s["rows"]
    names = [r["condition"].replace("NoRevocation", "NoRevocation*").replace("CLR+Reconstruct", "CLR+Reconstruct") for r in rows]
    panels = [("stale_selection", "(a) Stale selection (E1)", RED),
              ("utility", "(b) Correct choice (E2)", BLUE),
              ("audit_admission_correct", "(c) Admission audit", GREEN)]
    fig, axes = plt.subplots(1, 3, figsize=(6.05, 2.5), sharey=True)
    for ax, (key, title, col) in zip(axes, panels):
        for i, r in enumerate(rows):
            d = r[key]; c = GREY if (r["condition"] == "NoRevocation" and key == "stale_selection") else col
            ax.errorbar(d["mean"], i, xerr=[[max(0, d["mean"] - d["lower"])], [max(0, d["upper"] - d["mean"])]], fmt="o", color=c, capsize=2.5, ms=4.5, lw=1)
        ax.set_xlim(-0.05, 1.05); ax.set_xticks([0, 0.5, 1], ["0", "0.5", "1"]); ax.set_title(title)
        ax.set_xlabel("fraction of 100 tasks"); ax.grid(axis="x", color="#DDDDDD", lw=0.5)
    axes[0].set_yticks(range(len(rows)), names); axes[0].invert_yaxis()
    fig.text(0.5, 0.01, "* Under NoRevocation the designated supplier is still permitted, so E1 is the correct choice there.", ha="center", fontsize=8)
    fig.tight_layout(pad=0.4, w_pad=0.8, rect=(0, 0.06, 1, 1)); fig.savefig(OUT / "decision_harm.pdf"); plt.close(fig)

robustness(); decision()
