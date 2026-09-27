"""Generate the model scaling table for K=1..4."""

from __future__ import annotations

import json

from apr.explorer import model_result
from apr.model import TransitionSystem
from apr.policies import Configuration

from common import GENERATED, provenance, write_csv, write_json, write_latex, write_markdown


def run() -> list[dict[str, object]]:
    rows = []
    for sources in range(1, 5):
        governed = model_result(TransitionSystem(Configuration.GOVERNED, sources=sources))
        deleted = model_result(TransitionSystem(Configuration.DELETE_EVIDENCE, sources=sources))
        rows.append({
            "sources": sources,
            "states": governed["state_count_s0"],
            "transitions": governed["transitions"],
            "product_states": governed["product_states"],
            "delete_evidence_review_failures": deleted["review_failures"],
        })
    write_json(GENERATED / "table5.json", {"rows": rows, "metadata": provenance(experiment="table5", inputs={"sources": [1, 2, 3, 4]})})
    write_csv(GENERATED / "table5.csv", rows)
    write_markdown(GENERATED / "table5.md", rows)
    write_latex(GENERATED / "table5.tex", rows)
    write_json(GENERATED / "table5.metadata.json", provenance(experiment="table5", inputs={"sources": [1, 2, 3, 4]}))
    return rows


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
