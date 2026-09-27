"""Compare generated results with manuscript assertions and write an audit."""

from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_ROOT = Path(os.environ.get("APR_REPORT_ROOT", str(ROOT)))


def compare_table4() -> list[dict[str, object]]:
    generated = json.loads((ROOT / "results/generated/table4.json").read_text(encoding="utf-8"))["rows"]
    expected = json.loads((ROOT / "results/expected/table4.json").read_text(encoding="utf-8"))
    checks = []
    fields = ["state_count_s0", "state_count_s1", "transitions", "information_safety", "authorization_safety", "review_failures", "product_states", "synchronous_observations", "payload_only", "witness_length"]
    for row in generated:
        target = expected[row["configuration"]]
        for field in fields:
            observed = row[field]
            wanted = target[field]
            checks.append({"configuration": row["configuration"], "field": field, "expected": wanted, "observed": observed, "status": "MATCH" if observed == wanted else "RESULT MISMATCH"})
    return checks


def compare_table5() -> list[dict[str, object]]:
    generated = json.loads((ROOT / "results/generated/table5.json").read_text(encoding="utf-8"))["rows"]
    expected = json.loads((ROOT / "results/expected/table5.json").read_text(encoding="utf-8"))
    fields = ["states", "transitions", "product_states", "delete_evidence_review_failures"]
    return [{"configuration": f"K={row['sources']}", "field": field, "expected": expected[str(row["sources"])][field], "observed": row[field], "status": "MATCH" if row[field] == expected[str(row["sources"])][field] else "RESULT MISMATCH"} for row in generated for field in fields]


def compare_table6() -> list[dict[str, object]]:
    generated = json.loads((ROOT / "results/generated/table6.json").read_text(encoding="utf-8"))["rows"]
    expected = json.loads((ROOT / "results/expected/table6.json").read_text(encoding="utf-8"))
    checks = []
    for row in generated:
        target = expected[row["recorder"]][row["question"]]
        for field, expected_field in (("verdict", "verdict"), ("explored_product_nodes", "explored_nodes")):
            checks.append({"configuration": f"{row['recorder']}/{row['question']}", "field": field, "expected": target[expected_field], "observed": row[field], "status": "MATCH" if row[field] == target[expected_field] else "RESULT MISMATCH"})
    return checks


def compare_question_bounds() -> list[dict[str, object]]:
    generated = json.loads((ROOT / "results/generated/question_class_bounds.json").read_text(encoding="utf-8"))["rows"][-1]
    expected = json.loads((ROOT / "results/expected/question_class_bounds.json").read_text(encoding="utf-8"))
    return [{"configuration": "K=3", "field": field, "expected": expected[field], "observed": generated[field], "status": "MATCH" if generated[field] == expected[field] else "RESULT MISMATCH"} for field in ("pre_cut_histories", "operational_view_fibers", "admission_bits", "enforcement_order_bits", "final_state_bits", "full_ex_post_bits")]


def compare_table7() -> list[dict[str, object]]:
    generated = json.loads((ROOT / "results/generated/table7.json").read_text(encoding="utf-8"))["rows"]
    expected = json.loads((ROOT / "results/expected/table7.json").read_text(encoding="utf-8"))["rows"]
    checks = []
    for row in generated:
        target = expected[f"{row['use_probability']:.2f}"]
        for field in ("quarantined", "truly_dependent", "over_quarantine_ratio", "withheld_clean"):
            # The manuscript gives stochastic means, not a portable exact
            # regression. Exact comparison is still recorded as an assertion.
            checks.append({"configuration": f"u={row['use_probability']:.2f}", "field": field, "expected": target[field], "observed": row[field], "status": "MATCH" if abs(row[field] - target[field]) < 1e-12 else "RESULT MISMATCH"})
    return checks


def main() -> dict[str, object]:
    checks = compare_table4() + compare_table5() + compare_table6() + compare_question_bounds() + compare_table7()
    mismatches = [check for check in checks if check["status"] != "MATCH"]
    report_lines = [
        "# Manuscript consistency report",
        "",
        "This report is generated from the executable artifact. Expected paper values are read from `results/expected/`; they are never used by the model.",
        "",
        "## Current revision reconstruction checks",
        "",
        "| Configuration | Field | Expected reconstruction value | Observed | Status |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    report_lines.extend(f"| {check['configuration']} | {check['field']} | {check['expected']} | {check['observed']} | {check['status']} |" for check in checks)
    report_lines.extend([
        "",
        "## Specification and environment findings",
        "",
        "| Category | Manuscript location | Evidence | Recommended action |",
        "| --- | --- | --- | --- |",
        "| PROVENANCE | Section 7.2 | The historical checker pair, TLC runtime, original seeds, and original recorder automata were not supplied. | The manuscript now identifies the Python output as an independent reconstruction and makes no Python/TLC agreement claim. |",
        "| TLC STATUS | Section 7.2 | TLC was unavailable in the current environment. | The TLA+ files remain a separately documented reference specification; TLC validation is pending external execution. |",
        "| HISTORICAL VALUES | Sections 7.3–7.5 | Earlier paper assertions are preserved under `results/historical_paper_assertions/`. | Current tables and figures use the generated reconstruction values. |",
        "| STOCHASTIC PROVENANCE | Section 7.5 | Historical seeds were not supplied. | The current generator uses declared seeds and labels the results as reconstruction evidence. |",
        "",
        f"Generated reconstruction checks: {len(checks)}; matches: {len(checks) - len(mismatches)}; unexplained mismatches: {len(mismatches)}.",
    ])
    output = "\n".join(report_lines) + "\n"
    (REPORT_ROOT / "docs/MANUSCRIPT_CONSISTENCY_REPORT.md").parent.mkdir(parents=True, exist_ok=True)
    (REPORT_ROOT / "docs/MANUSCRIPT_CONSISTENCY_REPORT.md").write_text(output, encoding="utf-8")
    result = {"checks": checks, "mismatch_count": len(mismatches)}
    (REPORT_ROOT / "results/generated").mkdir(parents=True, exist_ok=True)
    (REPORT_ROOT / "results/generated/manuscript_comparison.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
