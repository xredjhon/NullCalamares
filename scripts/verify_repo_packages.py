from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog" / "packages" / "repo.json"
OUTPUT = ROOT / "dist" / "reports" / "repo-availability.json"


def main() -> None:
    items = json.loads(CATALOG.read_text(encoding="utf-8"))
    packages = []
    for item in items:
        for package in item["packages"]:
            if package not in packages:
                packages.append(package)
    result = {"available": [], "missing": [], "checked": len(packages)}
    for package in packages:
        proc = subprocess.run(
            ["pacman", "-Si", package],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if proc.returncode == 0:
            result["available"].append(package)
        else:
            result["missing"].append(package)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    if result["missing"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
