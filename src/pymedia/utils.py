from datetime import timedelta
from fractions import Fraction
from pathlib import Path

from pymedia.domain.errors import InvalidTrimPointsError


def parse_fraction(value: str | None) -> Fraction | None:
    """Convierte '25/1' a Fraction(25, 1)."""
    if not value or value == "0/0":
        return None
    num, _, den = value.partition("/")
    try:
        return Fraction(int(num), int(den))
    except (ValueError, ZeroDivisionError):
        return None


def to_int(value: str | int | None) -> int | None:
    """Convierte strings numéricos a int."""
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def to_float(value: str | float | None) -> float | None:
    """Convierte strings numéricos a float."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def parse_crop(value: str | None) -> tuple[int, int, int, int] | None:
    """Parsea 'IZQ,DER,ARRIBA,ABAJO' a una tupla de 4 enteros ≥ 0."""
    if value is None:
        return None

    try:
        left, right, top, bottom = (int(v) for v in value.split(","))
    except ValueError:
        return None

    if min(left, right, top, bottom) < 0:
        return None

    return left, right, top, bottom


def convert_to_timedelta(total_time: str) -> timedelta | None:
    """Convierte 'hh:mm:ss', 'mm:ss' o 'ss' a timedelta."""
    parts = total_time.split(":")
    if not all(p.isdigit() for p in parts):
        return None
    match tuple(map(float, parts)):
        case (hours, minutes, seconds):
            return timedelta(hours=hours, minutes=minutes, seconds=seconds)
        case (minutes, seconds):
            return timedelta(minutes=minutes, seconds=seconds)
        case (seconds,):
            return timedelta(seconds=seconds)
        case _:
            return None


def parse_trim_points(values: str | None) -> list[timedelta] | None:
    """Parsea lista de puntos de corte en str a lista timedelta."""
    if values is None:
        return None

    times_timedelta: list[timedelta] = []

    for v in values.split(","):
        t = convert_to_timedelta(v)
        if t is None:
            raise InvalidTrimPointsError(f"Formato no válido: {v}")
        times_timedelta.append(t)

    return times_timedelta


def resolve_output_path(
    output_name: str | None,
    source_path: Path,
    default_suffix: str,
) -> Path:
    """Resuelve la ruta de salida, creando directorio padre si necesario.

    Si output_name es None, genera un nombre por defecto basado en el archivo
    fuente. Si output_name incluye directorios, los crea si no existen.
    """
    if output_name is None:
        return Path(source_path.stem + default_suffix + source_path.suffix)
    out = Path(output_name)
    parent = out.parent
    if str(parent) != ".":
        parent.mkdir(parents=True, exist_ok=True)
    return out
