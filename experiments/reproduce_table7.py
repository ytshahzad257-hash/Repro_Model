"""Run the deterministic synthetic CLR quarantine experiment."""

from __future__ import annotations

import json

from apr.quarantine import run_quarantine_experiment

from common import GENERATED, load_seeds, provenance, write_csv, write_json, write_latex, write_markdown


def run(*, workflows_per_setting: int = 2000) -> list[dict[str, object]]:
    seed_config = load_seeds()
    root_seed = int(seed_config["quarantine_stream_seed"])
    workflow_seeds = [root_seed + index for index in range(workflows_per_setting)]
    rows = run_quarantine_experiment(seeds=workflow_seeds, sources=20, derived=100)
    growth_rows = []
    for index, derived in enumerate((20, 40, 60, 80, 100, 120, 140, 160, 180)):
        growth = run_quarantine_experiment(seeds=[root_seed + 10_000 + index * workflows_per_setting + offset for offset in range(workflows_per_setting)], use_probabilities=(0.5,), sources=20, derived=derived)
        growth_rows.extend({**row, "derived": derived} for row in growth)
    inputs = {"sources": 20, "derived": 100, "restricted_probability": 0.1, "fanin": 3, "workflows_per_setting": workflows_per_setting, "growth_settings": 9}
    metadata = provenance(experiment="table7_quarantine", inputs=inputs, seed=root_seed)
    write_json(GENERATED / "table7.json", {"rows": rows, "metadata": metadata, "total_workflows": workflows_per_setting * 14, "growth_rows": growth_rows})
    write_csv(GENERATED / "table7.csv", rows)
    write_markdown(GENERATED / "table7.md", rows)
    write_latex(GENERATED / "table7.tex", rows)
    write_json(GENERATED / "table7.metadata.json", metadata)
    return rows


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
