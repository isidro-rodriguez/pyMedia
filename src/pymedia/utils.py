"""Utilidades compartidas por los modelos de pyMedia."""

import math
import re
from datetime import UTC, datetime, timedelta
from email.utils import parsedate_to_datetime
from fractions import Fraction
from pathlib import Path
from typing import Any, cast

_CLOCK_RE = re.compile(r"(\d+):([0-5]?\d):([0-5]?\d(?:\.\d+)?)")
# Cota holgada (~31.700 años) para no desbordar timedelta con datos corruptos.
_MAX_SECONDS = 1e12


def parse_date(raw: str | None) -> datetime | None:
    """Convierte fechas habituales de metadatos multimedia a datetime formato ISO-8601.

    Args:
        raw: String a ser parseado como fecha.

    Returns:
        La fecha en formato ISO-8601, o `None` si la conversión falla.
    """
    if not raw:
        return None

    # ISO 8601
    if raw.endswith(("Z", "z")):
        raw = raw[:-1] + "+00:00"

    try:
        dt = datetime.fromisoformat(raw)
        return datetime(dt.year, dt.month, dt.day)
    except ValueError:
        pass

    # RFC 2822 / RFC 5322 / formatos similares
    try:
        dt = parsedate_to_datetime(raw)
        return datetime(dt.year, dt.month, dt.day)
    except (TypeError, ValueError, OverflowError):
        pass

    # Formatos con nombres de mes
    for fmt in (
        "%a %b %d %H:%M:%S %Y",
        "%b %d %H:%M:%S %Y",
        "%b %d %Y",
        "%d %b %Y",
        "%d %B %Y",
        "%B %d %Y",
    ):
        try:
            dt = datetime.strptime(raw, fmt)
            return datetime(dt.year, dt.month, dt.day)
        except ValueError:
            pass

    # Formatos numéricos no ISO.
    # Evitamos deliberadamente formatos ambiguos como 01/02/2024.
    for fmt in (
        "%Y/%m/%d",
        "%Y.%m.%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%d.%m.%Y",
    ):
        try:
            dt = datetime.strptime(raw, fmt)
            return datetime(dt.year, dt.month, dt.day)
        except ValueError:
            pass

    # Unix timestamp en segundos.
    if re.fullmatch(r"\d{9,11}", raw):
        try:
            timestamp = int(raw)
            dt = datetime.fromtimestamp(timestamp, tz=UTC)
            if 1970 <= dt.year <= 2100:
                return datetime(dt.year, dt.month, dt.day)
        except (ValueError, OverflowError, OSError):
            pass

    return None


def parse_fraction(value: str | None) -> Fraction | None:
    """Convierte '25/1' a Fraction(25, 1).

    Args:
        value: Texto con formato `num/den`; `None` o `0/0` devuelven `None`.

    Returns:
        La fracción parseada, o `None` si no es válida.
    """
    if not value or value == "0/0":
        return None

    num, _, den = value.partition("/")
    try:
        return Fraction(int(num), int(den))
    except (ValueError, ZeroDivisionError):
        return None


def parse_duration(value: object) -> timedelta | None:
    """Convierte una duración de ffprobe (`segundos` o `HH:MM:SS.ffffff`).

    Args:
        value: Texto con la duración; cualquier otro tipo devuelve `None`.

    Returns:
        La duración, o `None` si está ausente, mal formada, negativa o desmesurada.
    """
    if not isinstance(value, str):
        return None

    text = value.strip()
    match = _CLOCK_RE.fullmatch(text)
    if match:
        hours, minutes, seconds = match.groups()
        total = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    else:
        total = to_float(text)

    if total is None or total < 0:
        return None
    return to_timedelta(total)


def parse_r128_gain(value: str | None) -> float | None:
    """Convierte `R128_TRACK_GAIN` (Q7.8, referido a -23 LUFS) en LUFS integradas.

    Args:
        value: Texto con la ganancia en unidades de 1/256 dB.

    Returns:
        La sonoridad integrada en LUFS, o `None` si el valor no es válido.
    """
    gain = to_int(value)
    return None if gain is None else -23.0 + gain / 256


def parse_replaygain_gain(value: str | None) -> float | None:
    """Extrae el valor en dB de una etiqueta ReplayGain (p. ej. `-3.50 dB`).

    Args:
        value: Texto de la etiqueta.

    Returns:
        La ganancia en dB, o `None` si la etiqueta está vacía o no es numérica.
    """
    parts = value.split() if value else []
    return to_float(parts[0]) if parts else None


def parse_quantity(value: int | float | Fraction, locale: str) -> str:
    """Formatea una cantidad numérica según los separadores del locale.

    Args:
        value: Cantidad a formatear (entero, flotante o fracción).
        locale: Código de idioma (`"es"` o `"en"`) que determina los separadores.

    Returns:
        La cantidad formateada como texto.
    """
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
    """Formatea el texto que muestra el tamaño del vídeo.

    Args:
        size_bytes: Tamaño en bytes.
        locale: Código de idioma (`"es"` o `"en"`) para los separadores.

    Returns:
        Tamaño legible (GB/MB) acompañado del valor exacto en bytes.
    """
    size_gb = parse_quantity(value=size_bytes / 1024**3, locale=locale)
    size_mb = parse_quantity(value=size_bytes / 1024**2, locale=locale)
    size_bt = parse_quantity(value=size_bytes, locale=locale)

    if size_bytes > 1024**3:
        return f"{size_gb} GB ({size_bt} bytes)"
    return f"{size_mb} MB ({size_bt} bytes)"


def parse_timedelta(time: timedelta) -> str:
    """Formatea un objeto timedelta a una cadena con formato HH:MM:SS o MM:SS.

    Args:
        time: Duración a formatear.

    Returns:
        Texto en formato `H:MM:SS` o `MM:SS`.
    """
    total = int(time.total_seconds())
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def ticks_to_timedelta(
    ticks: str | int | None, time_base: Fraction | None
) -> timedelta | None:
    """Convierte un instante en unidades de `time_base` a timedelta.

    Args:
        ticks: Instante expresado en unidades de `time_base`.
        time_base: Duración en segundos de cada unidad (p. ej. `1/1000`).

    Returns:
        La duración, o `None` si falta algún dato o no es válido.
    """
    count = to_int(ticks)
    if count is None or time_base is None:
        return None
    return to_timedelta(float(count * time_base))


def to_bool(value: str | int | None) -> bool:
    """Interpreta un indicador numérico (`0`/`1`) como booleano.

    Args:
        value: Valor a convertir (texto numérico o entero).

    Returns:
        `True` si el valor es un entero distinto de cero; `False` en otro caso.
    """
    return bool(to_int(value))


def to_dict(value: object) -> dict[str, Any]:
    """Devuelve el valor si es un diccionario.

    Args:
        value: Valor a comprobar.

    Returns:
        El propio `value` si es un `dict`; un diccionario vacío en otro caso.
    """
    if isinstance(value, dict):
        return cast(dict[str, Any], value)
    return cast(dict[str, Any], {})


def to_dict_list(value: object) -> list[dict[str, Any]]:
    """Filtra los elementos diccionario de una lista.

    Args:
        value: Valor a comprobar.

    Returns:
        Los elementos `dict` de `value` si es una lista; una lista vacía en otro caso.
    """
    if not isinstance(value, list):
        return cast(list[dict[str, Any]], [])
    return cast(
        list[dict[str, Any]], [item for item in value if isinstance(item, dict)]
    )


def to_ffmpeg_value(value: str | Path) -> str:
    """Escapa una ruta o un texto para incrustarlo como valor de un filtro ffmpeg.

    El valor se entrega como token de filtergraph: los metacaracteres (separadores
    de filtro y de etiquetas, separadores de opciones, comillas y espacios) se
    escapan con barra invertida. No se entrecomilla porque ffmpeg no admite
    comillas simples anidadas ni escapes dentro de ellas, de modo que un texto con
    `'` no es representable entrecomillado.

    Args:
        value: Ruta o texto a usar como valor de un filtro.

    Returns:
        Valor posix (si es `Path`) con los metacaracteres escapados.
    """
    text = value.as_posix() if isinstance(value, Path) else value  # \ a / en rutas
    meta_chars = "\\':,;[]= "  # el espacio va incluido: ffmpeg recorta los extremos

    # ffmpeg des-escapa el valor dos veces (token del filtergraph y valor de la
    # opción), así que el escape se aplica una vez por nivel.
    for _ in range(2):
        text = "".join(f"\\{char}" if char in meta_chars else char for char in text)

    return text


def to_float(value: str | float | None) -> float | None:
    """Convierte strings numéricos a float.

    Args:
        value: Valor a convertir (texto numérico o flotante).

    Returns:
        El número convertido, o `None` si la conversión falla.
    """
    if value is None:
        return None

    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def to_int(value: str | int | None) -> int | None:
    """Convierte strings numéricos a int.

    Args:
        value: Valor a convertir (texto numérico o entero).

    Returns:
        El número convertido, o `None` si la conversión falla.
    """
    if value is None:
        return None

    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def to_text(value: object) -> str | None:
    """Devuelve el valor si es un texto no vacío.

    Args:
        value: Valor a comprobar.

    Returns:
        El propio `value` si es un `str` no vacío; `None` en otro caso.
    """
    return value if isinstance(value, str) and value else None


def to_timedelta(seconds: float | None) -> timedelta | None:
    """Convierte segundos a timedelta.

    Args:
        seconds: Número de segundos.

    Returns:
        La duración, o `None` si el valor falta, no es finito o es desmesurado.
    """
    if seconds is None or not math.isfinite(seconds) or abs(seconds) > _MAX_SECONDS:
        return None
    return timedelta(seconds=seconds)
