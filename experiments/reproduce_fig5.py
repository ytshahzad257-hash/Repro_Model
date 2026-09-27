"""Generate Figure 5 from question-class bound output."""

from __future__ import annotations

import json

from apr.plotting import Series, line_plot
from common import FIGURES, ensure_outputs
from question_bounds import run


def plot() -> None:
    ensure_outputs()
    rows = run()
    x = [row["sources"] for row in rows]
    series = tuple(Series(label, tuple(float(row[field]) for row in rows), color) for field, label, color in (("admission_bits", "Admission", "#1f77b4"), ("enforcement_order_bits", "Enforcement order", "#d62728"), ("final_state_bits", "Final state", "#2ca02c"), ("full_ex_post_bits", "Full ex post", "#9467bd")))
    line_plot(FIGURES / "fig5.svg", FIGURES / "fig5.png", title="Question-relative evidence bounds", x_label="Restricted sources K", y_label="Private bits required", x_values=tuple(float(value) for value in x), series=series)


if __name__ == "__main__":
    plot()
