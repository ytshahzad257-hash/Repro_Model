"""Generate Figure 9 from synthetic quarantine output."""

from __future__ import annotations

import json

from apr.plotting import Series, line_plot
from common import FIGURES, GENERATED, ensure_outputs, load_seeds
from reproduce_table7 import run


def plot() -> None:
    ensure_outputs()
    rows = run()
    import json
    generated = json.loads((GENERATED / "table7.json").read_text(encoding="utf-8"))
    growth_rows = generated["growth_rows"]
    x = [row["use_probability"] for row in rows]
    series = tuple(Series(label, tuple(float(row[field]) for row in rows), color, tuple(float(row[f"{field}_half_width"]) for row in rows)) for field, label, color in (("quarantined", "Quarantined", "#1f77b4"), ("truly_dependent", "Truly dependent", "#d62728"), ("withheld_clean", "Withheld although clean", "#2ca02c")))
    line_plot(FIGURES / "fig9.svg", FIGURES / "fig9.png", title="Conservative quarantine versus true dependence", x_label="Probability an admitted input is used", y_label="Share of derived items", x_values=tuple(float(value) for value in x), series=series)
    gx = tuple(float(row["derived"]) for row in growth_rows) if growth_rows and "derived" in growth_rows[0] else tuple(float(index) for index, _ in enumerate(growth_rows))
    if growth_rows:
        growth_series = tuple(Series(label, tuple(float(row[field]) for row in growth_rows), color) for field, label, color in (("quarantined", "Quarantined", "#1f77b4"), ("truly_dependent", "Truly dependent", "#d62728"), ("withheld_clean", "Withheld although clean", "#2ca02c")))
        line_plot(FIGURES / "fig9_growth.svg", FIGURES / "fig9_growth.png", title="Quarantine as derived memory grows", x_label="Derived items", y_label="Share of derived items", x_values=gx, series=growth_series)


if __name__ == "__main__":
    plot()
