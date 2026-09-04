"""Reversión temporal del auto-fix D413 de ruff (línea en blanco antes del cierre)."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = re.compile(r"^\s*(Args|Attributes|Returns|Raises|Yields|Params|Parameters|Example|Examples|Note|Notes):\s*$")

TARGETS = [
    ROOT / "src" / "pymedia",
    ROOT / "tests",
    ROOT / "scripts",
    ROOT / "build.py",
]


def revert_d413(path: Path) -> int:
    lines = path.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    changes = 0
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if (
            i + 1 < n
            and lines[i + 1].strip() in ('"""', "'''")
            and line.strip() == ""
            and i - 1 >= 0
            and lines[i - 1].strip() != ""
        ):
            # Buscar el docstring hacia atrás para ver si tiene secciones Google.
            has_section = False
            j = i - 1
            while j >= 0 and lines[j].strip() not in ('"""', "'''") and not lines[j].strip().startswith("def ") and not (
                lines[j].strip().startswith("class ")
            ):
                if SECTION.match(lines[j]):
                    has_section = True
                    break
                if lines[j].strip().endswith('"""') or lines[j].strip().endswith("'''"):
                    break
                j -= 1
            if has_section:
                changes += 1
                i += 1  # omite la línea en blanco: se revierte
                continue
        out.append(line)
        i += 1
    if changes:
        path.write_text("\n".join(out) + "\n", encoding="utf-8")
    return changes


def walk() -> None:
    total = 0
    files = []
    if TARGETS[-1].is_file():
        files.append(TARGETS[-1])
    for base in TARGETS[:-1]:
        files.extend(base.rglob("*.py"))
    for path in files:
        n = revert_d413(path)
        if n:
            total += n
            print(f"{path.relative_to(ROOT)}: {n} docstrings revertidos")
    print(f"TOTAL: {total}")


if __name__ == "__main__":
    walk()