"""Metadatos de una pista de audio."""

from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path


@dataclass(kw_only=True)
class AudioMetadata:
    """Metadatos de una pista de audio.

    Attributes:
        language: Código de idioma de la pista.
        title: Título de la pista.
        default: Si es la pista de audio por defecto del contenedor.
        forced: Si es una pista de reproducción forzada.
        hearing_impaired: Si es una pista orientada a personas con problemas auditivos.
        commentary: Si es una pista de comentarios de audio.
        dubbed: Si es una pista doblada (ffmpeg: "dub").
        original: Si es la pista original (ffmpeg: "original").
        lyrics: Si contiene letras (ffmpeg: "lyrics").
        karaoke: Si es una pista de karaoke (ffmpeg: "karaoke").
        visual_impaired: Si pista para discapacidad visual (ffmpeg: "visual_impaired").
        clean_effects: Si es una pista de efectos limpios (ffmpeg: "clean_effects").
    """

    language: str | None = None
    title: str | None = None
    default: bool | None = None
    forced: bool | None = None
    hearing_impaired: bool | None = None
    commentary: bool | None = None
    dubbed: bool | None = None
    original: bool | None = None
    lyrics: bool | None = None
    karaoke: bool | None = None
    visual_impaired: bool | None = None
    clean_effects: bool | None = None


@dataclass(kw_only=True, frozen=True, slots=True)
class Audio:
    """Información de una pista de audio.

    Attributes:
        path: Ruta al fichero de pista de audio.
        global_index: Número de emisión asignado en el contenedor.
        track_index: Índice en el listado de pistas de audio.
        codec: Nombre del códec de audio.
        duration: Duración de la pista de vídeo.
        sample_rate: Frecuencia de muestreo en Hz.
        channels: Número de canales.
        channel_layout: Distribución de canales (p. ej. "stereo").
        bit_rate: Tasa de bits en bps.
        metadata: Metadatos de la pista de audio.
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
    metadata: AudioMetadata = field(default_factory=AudioMetadata)
