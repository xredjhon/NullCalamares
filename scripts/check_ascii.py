from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "dist", "__pycache__"}
SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".woff", ".woff2"}


def should_skip(path: Path) -> bool:
    if any(part in SKIP_DIRS for part in path.parts):
        return True
    if path.suffix.lower() in SKIP_SUFFIXES:
        return True
    return False


def main() -> None:
    failures = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or should_skip(path):
            continue
        data = path.read_bytes()
        for line_no, line in enumerate(data.splitlines(), start=1):
            if any(byte > 127 for byte in line):
                failures.append(f"{path.relative_to(ROOT)}:{line_no}")
    if failures:
        raise SystemExit("\n".join(failures))


if __name__ == "__main__":
    main()
