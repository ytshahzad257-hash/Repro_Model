"""Run TLC when the reviewer supplies a local tla2tools.jar."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "generated" / "tlc_results.json"


def main() -> int:
    jar = os.environ.get("TLA2TOOLS_JAR")
    if not jar:
        candidate = ROOT / "tla2tools.jar"
        jar = str(candidate) if candidate.exists() else None
    if not jar or not Path(jar).exists():
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps({"status": "unavailable", "reason": "TLA2TOOLS_JAR was not supplied"}, indent=2) + "\n", encoding="utf-8")
        print("TLC unavailable: set TLA2TOOLS_JAR to a local tla2tools.jar")
        return 0
    config_dir = ROOT / "tla" / "configs"
    log_dir = ROOT / "results" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    runs = []
    for config_path in sorted(config_dir.glob("*.cfg")):
        module = ROOT / "tla" / "modules" / ("AuditPreservingRevocationProduct.tla" if config_path.name == "product.cfg" else "AuditPreservingRevocation.tla")
        command = ["java", "-cp", jar, "tlc2.TLC", str(module), "-config", str(config_path)]
        completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        log_path = log_dir / f"tlc_{config_path.stem}.log"
        log_path.write_text(completed.stdout + "\n" + completed.stderr, encoding="utf-8")
        runs.append({"configuration": config_path.stem, "returncode": completed.returncode, "log": str(log_path)})
    passed = all(run["returncode"] == 0 for run in runs)
    OUT.write_text(json.dumps({"status": "passed" if passed else "failed", "runs": runs}, indent=2) + "\n", encoding="utf-8")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
