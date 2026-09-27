"""Report available reproduction tooling without changing the environment."""

from __future__ import annotations

import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def version(command: list[str]) -> str | None:
    try:
        return subprocess.check_output(command, text=True, stderr=subprocess.STDOUT).strip().splitlines()[0]
    except (OSError, subprocess.CalledProcessError, IndexError):
        return None


def inspect_environment() -> dict[str, object]:
    return {
        "platform": platform.platform(),
        "python": sys.version,
        "java": version(["java", "-version"]),
        "java_path": shutil.which("java"),
        "tlc2tools_jar": str(Path(__file__).resolve().parents[1] / "tla2tools.jar") if (Path(__file__).resolve().parents[1] / "tla2tools.jar").exists() else None,
        "tla2tools_env": __import__("os").environ.get("TLA2TOOLS_JAR"),
    }


if __name__ == "__main__":
    print(json.dumps(inspect_environment(), indent=2))
