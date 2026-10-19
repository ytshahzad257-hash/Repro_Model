"""Table 6: Algorithm 1 for four recorders and three questions on the model."""

from __future__ import annotations

import json
import time

from apr.recorder_experiment import run_matrix

from common import GENERATED, provenance, write_csv, write_json, write_markdown

SOURCES = (1, 2, 3)


def run() -> list[dict[str, object]]:
    rows = []
    timings = {}
    for sources in SOURCES:
        started = time.perf_counter()
        rows.extend(run_matrix(sources))
        timings[sources] = round(time.perf_counter() - started, 2)
    by_k = {k: [(r["recorder"], r["question"], r["verdict"]) for r in rows if r["sources"] == k] for k in SOURCES}
    identical = all(by_k[k] == by_k[SOURCES[-1]] for k in SOURCES)
    metadata = provenance(experiment="table6_algorithm1", inputs={"sources": list(SOURCES), "configuration": "Governed"})
    write_json(GENERATED / "table6.json", {"rows": rows, "verdicts_identical_across_K": identical, "seconds": timings, "metadata": metadata})
    flat = [{k: v for k, v in row.items() if not k.startswith(("witness", "answer"))} for row in rows]
    write_csv(GENERATED / "table6.csv", flat)
    write_markdown(GENERATED / "table6.md", flat)
    for row in rows:
        if row["verdict"] == "insufficient":
            write_json(GENERATED / "witnesses" / f"table6_K{row['sources']}_{row['recorder']}_{row['question']}.json", row)
    return rows


if __name__ == "__main__":
    print(json.dumps(run(), indent=2)[:2000])
