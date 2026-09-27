"""Make a conservative anonymous copy of artifact text files."""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path


def main(source: str) -> None:
    root = Path(source)
    for path in root.rglob("*"):
        if not path.is_file() or path.name in {"anonymize_artifact.py"}:
            continue
        if path.suffix.lower() not in {".md", ".cff", ".json", ".toml", ".yml", ".yaml"}:
            continue
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"Muhammad Shahzad Khadim", "Anonymous Author", text)
        text = re.sub(r"Muhammad Muneer Umar", "Anonymous Author", text)
        text = re.sub(r"muneer\.umar@kust\.edu\.pk", "anonymous@example.invalid", text)
        path.write_text(text, encoding="utf-8")
    git_dir = root / ".git"
    if git_dir.exists():
        shutil.rmtree(git_dir)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python scripts/anonymize_artifact.py <copy>")
    main(sys.argv[1])
