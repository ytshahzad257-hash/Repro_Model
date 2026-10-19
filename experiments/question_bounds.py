"""Theorem 1 question-class bounds on the executable model (Figure 5(b))."""

from __future__ import annotations

import json

from apr.question_bounds import compute

from common import GENERATED, provenance, write_csv, write_json


def run() -> list[dict[str, object]]:
    rows = [compute(sources).as_row() for sources in (1, 2, 3)]
    larger_path = GENERATED / "larger_bounds.json"
    if larger_path.exists():
        larger = json.loads(larger_path.read_text())
        if larger["status"] == "complete": rows.append(larger["row"])
    metadata = provenance(experiment="question_class_bounds", inputs={"sources": [r["sources"] for r in rows], "configuration": "Governed",
                          "view": "projection onto Read[i], RequestRevoke, UpdatePolicy, FireEffect"})
    write_json(GENERATED / "question_class_bounds.json", {"rows": rows, "metadata": metadata})
    write_csv(GENERATED / "question_class_bounds.csv", rows)
    write_json(GENERATED / "question_class_bounds.metadata.json", metadata)
    return rows


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
