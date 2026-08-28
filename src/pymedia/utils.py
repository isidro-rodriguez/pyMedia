from fractions import Fraction
from pathlib import Path


def parse_fraction(value: str | None) -> Fraction | None:
    """Convierte '25/1' a Fraction(25, 1)."""
    if not value or value == "0/0":
        return None
    num, _, den = value.partition("/")
    try:
        return Fraction(int(num), int(den))
    except (ValueError, ZeroDivisionError):
        return None


def parse_quantity(value: int | float | Fraction, lang: str) -> str:
    if isinstance(value, Fraction):
        if value.denominator == 1:
            value = value.numerator
        else:
            value = float(value)

    if isinstance(value, int):
        result = f"{value:,}"
    else:
        result = f"{value:,.3f}"

    if lang == "en":
        return result
    return result.replace(",", "X").replace(".", ",").replace("X", ".")


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
