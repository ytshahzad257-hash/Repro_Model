"""Regression check of generated results against results/expected/revision5_1.json.

The expected file records the version 5 structural regression values.
It is never read by model code; it only detects unintended semantic changes.
Run with --update to rewrite it from the current generated results.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "results" / "generated"
EXPECTED = ROOT / "results" / "expected" / "revision5.json"
FIELDS = ("state_count_s0", "state_count_s1", "transitions_s0", "information_safety", "authorization_safety",
          "review_failures", "product_states", "product_transitions", "synchronous_observations", "payload_only", "witness_length", "transitions_s1", "equal_release_product_states", "equal_release_product_transitions", "equal_release_observations")


def snapshot() -> dict:
    matrix_doc = json.loads((GEN / "model_matrix.json").read_text())
    if not matrix_doc.get("complete"):
        raise RuntimeError("Refusing to check or update expectations from an incomplete matrix")
    matrix = matrix_doc["rows"]
    bounds = json.loads((GEN / "question_class_bounds.json").read_text())["rows"]
    t7 = json.loads((GEN / "table7.json").read_text())
    out = {
        "model": {r["case_id"]: {f: r[f] for f in FIELDS} for r in matrix},
        "bounds": bounds,
        "quarantine": {str(r["use_probability"]): round(r["quarantined"], 6) for r in t7["rows"]},
    }
    t6 = GEN / "table6.json"
    if t6.exists():
        out["sufficiency"] = {f"K{r['sources']}/{r['recorder']}/{r['question']}": [r["verdict"], r["explored_product_nodes"]]
                              for r in json.loads(t6.read_text())["rows"]}
    return out


def main() -> int:
    current = snapshot()
    if "--update" in sys.argv:
        cross = json.loads((GEN / "cross_checker_agreement.json").read_text())
        if cross["status"] != "PASS" or cross["configurations_x_K"] != len(current["model"]):
            raise RuntimeError("Expected update requires a passing, coverage-matched cross-check")
        EXPECTED.write_text(json.dumps(current, indent=1, sort_keys=True) + "\n")
        print("updated", EXPECTED)
        return 0
    expected = json.loads(EXPECTED.read_text())
    mismatches = [key for key in set(expected) | set(current) if key not in expected or key not in current or expected[key] != current[key]
                  and not (key == "quarantine" and len(json.loads((GEN / "table7.json").read_text())["rows"]) and
                           json.loads((GEN / "table7.json").read_text())["metadata"]["inputs"]["workflows_per_setting"] != 2000)]
    if mismatches:
        print("MISMATCH in", mismatches)
        return 1
    print("all expected values match")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
