"""Generate the finite-model configuration table from the Python explorer."""

from __future__ import annotations

import json

from apr.explorer import model_result
from apr.model import TransitionSystem
from apr.policies import Configuration

from common import GENERATED, ensure_outputs, provenance, write_csv, write_json, write_latex, write_markdown


def run() -> list[dict[str, object]]:
    rows = [model_result(TransitionSystem(configuration, sources=1)) for configuration in Configuration]
    ensure_outputs()
    write_json(GENERATED / "table4.json", {"rows": rows, "metadata": provenance(experiment="table4", inputs={"sources": 1})})
    write_csv(GENERATED / "table4.csv", rows)
    write_markdown(GENERATED / "table4.md", rows)
    write_latex(GENERATED / "table4.tex", rows)
    write_json(GENERATED / "table4.metadata.json", provenance(experiment="table4", inputs={"sources": 1}))
    return rows


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
