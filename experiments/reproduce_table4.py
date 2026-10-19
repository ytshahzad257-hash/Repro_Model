"""Table 4 (K = 1) from the Python explorer."""

from __future__ import annotations

import json

from apr.policies import Configuration
from model_matrix import row_for
from finite_cases import cases

from common import GENERATED, ensure_outputs, provenance, write_csv, write_json, write_markdown


def run() -> list[dict[str, object]]:
    ensure_outputs()
    matrix_path = GENERATED / "model_matrix.json"
    rows = [r for r in json.loads(matrix_path.read_text())["rows"] if r["sources"] == 1 and r["secrets"] == "shared"]
    metadata = provenance(experiment="table4", inputs={"sources": 1})
    write_json(GENERATED / "table4.json", {"rows": rows, "metadata": metadata})
    flat = [{k: v for k, v in row.items() if k not in ("witness_left", "witness_right")} for row in rows]
    write_csv(GENERATED / "table4.csv", flat)
    write_markdown(GENERATED / "table4.md", flat)
    for row in rows:
        if row["witness_left"]:
            write_json(GENERATED / "witnesses" / f"table4_{row['configuration']}.json", {k: row[k] for k in ("configuration", "witness_length", "witness_left", "witness_right")})
    return rows


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
