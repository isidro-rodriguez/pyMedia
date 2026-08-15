from datetime import timedelta
from fractions import Fraction


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
    """
    Convierte 'hh:mm:ss', 'mm:ss' o 'ss' a timedelta.
    Soporta formato negativo: '-1:00' o '-45'.
    """
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
