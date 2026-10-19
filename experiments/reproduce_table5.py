"""Table 5 (scaling of the Governed configuration) from the model matrix."""

from __future__ import annotations

import json

from common import GENERATED, provenance, write_csv, write_json, write_markdown


def run() -> list[dict[str, object]]:
    matrix = json.loads((GENERATED / "model_matrix.json").read_text(encoding="utf-8"))["rows"]
    tlc_path = GENERATED / "tlc_matrix.json"
    tlc = {(r["configuration"], r["sources"]): r for r in json.loads(tlc_path.read_text(encoding="utf-8"))["rows"] if r.get("secrets", "shared") == "shared"} if tlc_path.exists() else {}
    rows = []
    matrix = [r for r in matrix if r.get("secrets", "shared") == "shared"]
    for k in sorted({r["sources"] for r in matrix}):
        governed = next(r for r in matrix if r["configuration"] == "Governed" and r["sources"] == k)
        deleted = next(r for r in matrix if r["configuration"] == "DeleteEvidence" and r["sources"] == k)
        rows.append({
            "sources": k,
            "states": governed["state_count_s0"],
            "transitions": governed["transitions_s0"],
            "product_states": governed["product_states"],
            "explorer_seconds_both_secrets": governed["explorer_seconds_single_both_secrets"],
            "tlc_seconds_s0": tlc.get(("Governed", k), {}).get("tlc_seconds_s0_count"),
            "delete_evidence_review_failures": deleted["review_failures"],
        })
    write_json(GENERATED / "table5.json", {"rows": rows, "metadata": provenance(experiment="table5", inputs={"sources": [1, 2, 3, 4]})})
    write_csv(GENERATED / "table5.csv", rows)
    write_markdown(GENERATED / "table5.md", rows)
    return rows


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
