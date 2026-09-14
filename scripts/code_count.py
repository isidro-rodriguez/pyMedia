"""Conteo de líneas de código de pyMedia.

Cuenta las líneas efectivas (sin líneas en blanco ni comentarios) y las
agrupa por categoría: scripts, tests, data, locales y lógica (el resto
de `src/pymedia`).

Uso:
    uv run python scripts/code_count.py
"""

from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "pymedia"

# Extensiones que cuentan como código: Python y catálogos gettext.
CODE_EXTENSIONS = {".py", ".po", ".pot"}


@dataclass
class Category:
    """Grupo de ficheros con su total de líneas de código."""

    name: str
    files: list[tuple[Path, int]] = field(default_factory=list)

    @property
    def total(self) -> int:
        """Suma de líneas de código de todos sus ficheros."""
        return sum(count for _, count in self.files)


def _is_blank_or_comment(line: str) -> bool:
    """Indica si la línea está vacía o es solo un comentario."""
    stripped = line.strip()
    return not stripped or stripped.startswith("#")


def count_code_lines(path: Path) -> int:
    """Cuenta las líneas de código de un fichero.

    Args:
        path: Fichero de texto (Python, `.po`, `.pot`...).

    Returns:
        Número de líneas no vacías y sin comentarios.
    """
    with path.open("r", encoding="utf-8", errors="replace") as f:
        return sum(1 for line in f if not _is_blank_or_comment(line))


def _files_with_exts(base: Path, extensions: set[str]) -> Iterator[Path]:
    """Genera los ficheros de `base` con extensión en `extensions`.

    Args:
        base: Directorio raíz del que buscar (recursivo).
        extensions: Extensiones permitidas, con punto y en minúsculas.

    Yields:
        Rutas de ficheros ordenadas por ruta relativa.
    """
    if not base.is_dir():
        return
    for path in sorted(base.rglob("*")):
        if path.is_file() and path.suffix.lower() in extensions:
            yield path


def _py_files(base: Path) -> Iterator[Path]:
    """Genera los ficheros Python de `base` (recursivo)."""
    return _files_with_exts(base, {".py"})


def _all_py_under_src() -> list[Path]:
    """Lista todos los `.py` de `src/pymedia` ordenados."""
    return sorted(_py_files(SRC))


def _in_dir(path: Path, directory: Path) -> bool:
    """Indica si `path` cuelga de `directory` (o es el propio directorio)."""
    return directory in path.parents


def build_categories() -> list[Category]:
    """Construye las categorías de conteo y sus ficheros.

    Returns:
        Lista de categorías en orden de presentación, cada una con sus
        ficheros y líneas de código ya contadas.
    """
    data_dir = SRC / "data"
    locales_dir = SRC / "locales"

    definitions = [
        ("scripts", list(_py_files(ROOT / "scripts"))),
        ("tests", list(_py_files(ROOT / "tests"))),
        (
            "data",
            list(_py_files(data_dir)),
        ),
        (
            "locales",
            list(_files_with_exts(locales_dir, CODE_EXTENSIONS)),
        ),
        (
            "lógica (src)",
            [
                path
                for path in _all_py_under_src()
                if not _in_dir(path, data_dir) and not _in_dir(path, locales_dir)
            ],
        ),
    ]

    categories = []
    for name, files in definitions:
        counted = [(path, count_code_lines(path)) for path in files]
        categories.append(Category(name=name, files=counted))
    return categories


def _print_category(category: Category) -> None:
    """Imprime el detalle de ficheros y el total de una categoría."""
    print(f"\n## {category.name} ({len(category.files)} ficheros)")
    for path, count in sorted(category.files, key=lambda item: -item[1]):
        relative = path.relative_to(ROOT)
        print(f"  {count:>6}  {relative}")
    print(f"  {'-' * 6}")
    print(f"  {category.total:>6}  total {category.name}")


def main() -> None:
    """Cuenta las líneas de código y muestra el informe por categorías."""
    categories = build_categories()
    for category in categories:
        _print_category(category)

    grand_total = sum(category.total for category in categories)
    total_files = sum(len(category.files) for category in categories)

    print(f"\n{'=' * 60}")
    for category in categories:
        print(f"  {category.name:<14} {category.total:>6}")
    print(f"  {'-' * 14}")
    print(f"  {'TOTAL':<14} {grand_total:>6}")
    print(f"\n  {total_files} ficheros, {grand_total} líneas de código")


if __name__ == "__main__":
    main()
