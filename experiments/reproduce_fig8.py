"""Generate the scaling figure from generated table 5."""

from __future__ import annotations

import json

from apr.explorer import explore, product_state_count
from apr.model import TransitionSystem
from apr.policies import Configuration

from apr.plotting import Series, line_plot
from common import FIGURES, GENERATED, ensure_outputs, provenance, write_json


def plot() -> None:
    ensure_outputs()
    rows = []
    for sources in range(1, 5):
        for configuration in Configuration:
            system = TransitionSystem(configuration, sources=sources)
            single = explore(system, 0)
            rows.append({"sources": sources, "configuration": configuration.value, "states": len(single.states), "product_states": product_state_count(system)})
    write_json(GENERATED / "figure8_data.json", {"rows": rows, "metadata": provenance(experiment="figure8", inputs={"sources": [1, 2, 3, 4]})})
    colors = ("#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e", "#1f77b4", "#d62728")
    single_series = []
    product_series = []
    for configuration in Configuration:
        selected = [row for row in rows if row["configuration"] == configuration.value]
        color = colors[len(single_series)]
        single_series.append(Series(configuration.value, tuple(float(row["states"]) for row in selected), color))
        product_series.append(Series(configuration.value, tuple(float(row["product_states"]) for row in selected), color))
    line_plot(FIGURES / "fig8.svg", FIGURES / "fig8.png", title="Finite-model state-space scaling", x_label="Restricted sources K", y_label="Distinct states", x_values=(1.0, 2.0, 3.0, 4.0), series=tuple(single_series))
    line_plot(FIGURES / "fig8_product.svg", FIGURES / "fig8_product.png", title="Self-composition product scaling", x_label="Restricted sources K", y_label="Product states", x_values=(1.0, 2.0, 3.0, 4.0), series=tuple(product_series))


if __name__ == "__main__":
    plot()
