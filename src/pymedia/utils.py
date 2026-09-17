"""Utilidades compartidas por los modelos de pyMedia."""

from datetime import timedelta
from fractions import Fraction
from pathlib import Path


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

    # ffmpeg desescapa el valor dos veces (token del filtergraph y valor de la
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
