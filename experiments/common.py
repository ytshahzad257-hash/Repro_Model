"""Shared, non-semantic experiment utilities."""

from __future__ import annotations

import csv
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "results" / "generated"
FIGURES = ROOT / "figures" / "generated"
SEEDS = ROOT / "experiments" / "seeds.json"


def load_seeds() -> dict[str, object]:
    return json.loads(SEEDS.read_text(encoding="utf-8"))


def git_revision() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def provenance(*, experiment: str, configuration: object = None, inputs: object = None, seed: object = None) -> dict[str, object]:
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_revision(),
        "python": sys.version,
        "platform": platform.platform(),
        "configuration": configuration,
        "inputs": inputs,
        "seed": seed,
        "experiment": experiment,
    }


def ensure_outputs() -> None:
    GENERATED.mkdir(parents=True, exist_ok=True)
    (GENERATED / "witnesses").mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, value: object) -> None:
    ensure_outputs()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: Iterable[dict[str, object]]) -> None:
    rows = list(rows)
    ensure_outputs()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    headers = list(rows[0])
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    lines.extend("| " + " | ".join(str(row.get(header, "")) for header in headers) + " |" for row in rows)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_latex(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    headers = list(rows[0])
    lines = ["\\begin{tabular}{" + "l" * len(headers) + "}", " \\toprule", " & ".join(headers) + " \\\\", " \\midrule"]
    lines.extend(" & ".join(str(row.get(header, "")).replace("_", "\\_") for header in headers) + " \\\\" for row in rows)
    lines.extend([" \\bottomrule", "\\end{tabular}"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
