import re
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


# Patrón: "SS", "MM:SS" o "HH:MM:SS" (segundos con decimales opcionales)
_TIMESTAMP_RE = re.compile(
    r"^(?:(?P<hours>\d+):)?(?P<minutes>\d+):(?P<seconds>\d+(?:\.\d+)?)$"
)


def parse_timestamp(value: str | None) -> timedelta | None:
    """Parsea 'HH:MM:SS', 'MM:SS' o 'SS' a timedelta."""
    if value is None:
        return None

    match = _TIMESTAMP_RE.fullmatch(value)
    if not match:
        return None

    parts = {k: float(v) for k, v in match.groupdict().items() if v}
    return timedelta(
        hours=parts.get("hours", 0),
        minutes=parts.get("minutes", 0),
        seconds=parts.get("seconds", 0),
    )


def parse_trim_points(values: str | None) -> list[timedelta] | None:
    """Parsea lista de puntos de corte en str a lista timedelta"""
    if values is None:
        return None

    times: list[timedelta] = []

    for v in values.split(","):
        timestamp = parse_timestamp(v)

        if not timestamp:
            return None

        times.append(timestamp)

    return times


def format_timedelta(td: timedelta) -> str:
    """Convierte timedelta a 'HH:MM:SS'."""
    total = int(td.total_seconds())
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"
