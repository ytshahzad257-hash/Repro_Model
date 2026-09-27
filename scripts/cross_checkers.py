"""Cross-check Python results against an optional TLC result export."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

from apr.explorer import model_result
from apr.model import TransitionSystem
from apr.policies import Configuration
from common import GENERATED, provenance, write_json


def run() -> dict[str, object]:
    python_rows = [model_result(TransitionSystem(configuration)) for configuration in Configuration]
    tlc_path = GENERATED / "tlc_results.json"
    tlc = json.loads(tlc_path.read_text(encoding="utf-8")) if tlc_path.exists() else {"status": "unavailable"}
    if tlc.get("status") != "passed":
        result = {"status": "WARNING", "reason": "TLC result export is unavailable; Python-only checks were generated.", "python_rows": python_rows, "tlc": tlc, "metadata": provenance(experiment="cross_checker")}
        write_json(GENERATED / "cross_checker_agreement.json", result)
        return result
    tlc_rows = tlc.get("rows")
    if not isinstance(tlc_rows, list):
        result = {"status": "WARNING", "reason": "TLC completed invariant checks but supplied no machine-readable state-count rows; Python/TLC numeric cross-check is pending.", "python_rows": python_rows, "tlc": tlc}
        write_json(GENERATED / "cross_checker_agreement.json", result)
        return result
    by_name = {row["configuration"]: row for row in tlc_rows}
    mismatches = []
    for row in python_rows:
        other = by_name.get(row["configuration"])
        for field in ("state_count_s0", "transitions", "information_safety", "authorization_safety", "review_failures", "product_states"):
            if other is None or row[field] != other.get(field):
                mismatches.append({"configuration": row["configuration"], "field": field, "python": row[field], "tlc": None if other is None else other.get(field)})
    result = {"status": "PASS" if not mismatches else "FAIL", "mismatches": mismatches, "python_rows": python_rows, "tlc": tlc, "metadata": provenance(experiment="cross_checker")}
    write_json(GENERATED / "cross_checker_agreement.json", result)
    return result


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
