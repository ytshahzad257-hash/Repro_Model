"""Build a deterministic source manifest and SHA-256 checksum list."""

from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifact"


def included(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    parts = set(relative.parts)
    if path.name == '.DS_Store':
        return False
    if parts & {".git", ".pytest_cache", "__pycache__", ".venv", "build", "dist"} or any(p.endswith(".egg-info") for p in parts):
        return False
    if relative.parts[:1] == ("artifact",):
        return False
    if relative.parts[:2] == ('figures','generated') and path.name != '.gitkeep':
        return False
    return path.is_file()


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def main() -> int:
    ARTIFACT.mkdir(parents=True, exist_ok=True)
    files = sorted((path for path in ROOT.rglob("*") if included(path)), key=lambda path: path.relative_to(ROOT).as_posix())
    lines = [
        "# Reproducibility artifact manifest",
        "",
        "This manifest covers source code, tests, TLA+ modules, expected assertions, technical documentation, saved experiment results and raw logs. Git internals and transient caches are excluded. Regenerate the manifest after repository changes.",
        "",
        f"Files covered: {len(files)}",
        "",
        "| Path | SHA-256 | Bytes |",
        "| --- | --- | ---: |",
    ]
    checksums = []
    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        checksum = digest(path)
        lines.append(f"| `{relative}` | `{checksum}` | {path.stat().st_size} |")
        checksums.append(f"{checksum}  {relative}")
    (ARTIFACT / "MANIFEST.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (ARTIFACT / "CHECKSUMS.txt").write_text("\n".join(checksums) + "\n", encoding="utf-8")
    print(f"wrote {len(files)} checksums")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
