from datetime import timedelta
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


def parse_quantity(value: int | float | Fraction, locale: str) -> str:
    """Convierte una cantidad (int | float | Fraction) str agrupado por miles y
    decimales según locale."""

    if isinstance(value, Fraction):
        if value.denominator == 1:
            value = value.numerator
        else:
            value = float(value)

    if isinstance(value, int):
        result = f"{value:,}"
    else:
        result = f"{value:,.3f}"

    if locale == "en":
        return result
    return result.replace(",", "X").replace(".", ",").replace("X", ".")


def parse_size(size_bytes: int, locale: str) -> str:
    """Formatea el texto que muestra el tamaño del vídeo."""

    size_gb = parse_quantity(value=size_bytes / 1024**3, locale=locale)
    size_mb = parse_quantity(value=size_bytes / 1024**2, locale=locale)
    size_bt = parse_quantity(value=size_bytes, locale=locale)

    if size_bytes > 1024**3:
        return f"{size_gb} GB ({size_bt} bytes)"
    return f"{size_mb} MB ({size_bt} bytes)"


def parse_timedelta(time: timedelta) -> str:
    """Formatea un objeto timedelta a una cadena con formato HH:MM:SS o MM:SS."""

    total = int(time.total_seconds())
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


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
