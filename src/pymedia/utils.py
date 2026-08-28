from fractions import Fraction
from pathlib import Path

from pymedia.errors import PyMediaError


def parse_fraction(value: str | None) -> Fraction | None:
    """Convierte '25/1' a Fraction(25, 1)."""
    if not value or value == "0/0":
        return None
    num, _, den = value.partition("/")
    try:
        return Fraction(int(num), int(den))
    except (ValueError, ZeroDivisionError):
        return None


def require[T](value: T | None, exc: PyMediaError) -> T:
    """
    Comprueba que un valor no sea None y lo devuelve ya validado.

    Args:
        value: Valor a comprobar.
        exc: Excepción a lanzar si `value` es None.

    Returns:
        El valor de entrada, con el tipo estrechado a no-None.

    Raises:
        PyMediaError: La excepción indicada en `exc`, si `value` es None.
    """
    if value is None:
        raise exc
    return value


def to_ffmpeg_path(path: Path) -> str:
    """Convierte una ruta a formato seguro para filtros ffmpeg (drawtext, etc.)."""
    posix = path.as_posix()  # normaliza \ a / (no-op en Linux/Mac)
    return posix.replace(":", r"\:")


def to_float(value: str | float | None) -> float | None:
    """Convierte strings numéricos a float."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def to_int(value: str | int | None) -> int | None:
    """Convierte strings numéricos a int."""
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None
