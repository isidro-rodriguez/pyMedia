"""Metadatos de una pista de audio."""

from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True, slots=True)
class Audio:
    """Metadatos de una pista de audio de un medio.

    Attributes:
        codec: Nombre del códec de audio.
        sample_rate: Frecuencia de muestreo en Hz.
        channels: Número de canales.
        channel_layout: Distribución de canales (p. ej. "stereo").
        bit_rate: Tasa de bits en bps.
        language: Código de idioma de la pista.
    """

    codec: str | None = None
    sample_rate: int | None = None
    channels: int | None = None
    channel_layout: str | None = None
    bit_rate: int | None = None
    language: str | None = None
