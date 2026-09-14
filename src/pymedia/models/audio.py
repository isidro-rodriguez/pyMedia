"""Metadatos de una pista de audio."""

from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path


@dataclass(frozen=True, kw_only=True, slots=True)
class Audio:
    """Metadatos de una pista de audio de un medio.

    Attributes:
        path: Ruta al fichero de pista de audio.
        global_index:  Número de emisión asignado en el contenedor.
        track_index: Índice en el listado de pistas de audio.
        codec: Nombre del códec de audio.
        duration: Duración de la pista de vídeo.
        sample_rate: Frecuencia de muestreo en Hz.
        channels: Número de canales.
        channel_layout: Distribución de canales (p. ej. "stereo").
        bit_rate: Tasa de bits en bps.
        language: Código de idioma de la pista.
        title: Titulo de la pista.
        default: Si es la pista de audio por defecto del contenedor.
        forced: Si es una pista de reproducción forzada.
        hearing_impaired: Si es una pista orientada a personas con problemas auditivos.
        commentary: Si es una pista de comentarios de audio.
    """

    path: Path
    global_index: int | None = None
    track_index: int | None = None
    codec: str | None = None
    duration: timedelta | None = None
    sample_rate: int | None = None
    channels: int | None = None
    channel_layout: str | None = None
    bit_rate: int | None = None
    language: str | None = None
    title: str | None = None
    default: bool | None = False
    forced: bool | None = False
    hearing_impaired: bool | None = False
    commentary: bool | None = False
