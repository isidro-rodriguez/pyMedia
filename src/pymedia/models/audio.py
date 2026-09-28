"""Información de una pista de audio."""

from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path


@dataclass(kw_only=True, frozen=True, slots=True)
class AudioFormat:
    """Propiedades técnicas del formato y codificación del flujo de audio.

    Attributes:
        codec: Nombre del códec de audio (p. ej. "aac", "ac3", "opus", "flac").
        sample_rate: Frecuencia de muestreo en Hertz (Hz) (p. ej. 44100, 48000).
        channels: Número de canales de audio (p. ej. 1, 2, 6).
        channel_layout: Distribución de canales ("mono", "stereo", "5.1(side)", ...).
        bit_rate: Tasa de bits de la pista en bits por segundo (bps).
    """

    codec: str | None = None
    sample_rate: int | None = None
    channels: int | None = None
    channel_layout: str | None = None
    bit_rate: int | None = None


@dataclass(kw_only=True, frozen=True, slots=True)
class AudioLoudness:
    """Métricas y metadatos de normalización y volumen (Loudness).

    Attributes:
        integrated: Sonoridad integrada según norma EBU R128 / ITU BS.1770 en LUFS.
        range: Rango dinámico de sonoridad (Loudness Range - LRA) en LU.
        true_peak: Pico verdadero máximo alcanzado en la señal en dBTP.
        replaygain_gain: Ganancia de ajuste recomendada por ReplayGain en dB.
        replaygain_peak: Valor pico de la muestra según ReplayGain.
    """

    integrated: float | None = None
    range: float | None = None
    true_peak: float | None = None
    replaygain_gain: float | None = None
    replaygain_peak: float | None = None


@dataclass(kw_only=True)
class AudioMetadata:
    """Etiquetas de metadatos descriptivos (clave-valor).

    Attributes:
        language: Código del idioma de la pista (p. ej. "spa", "eng", "jpn").
        title: Título o etiqueta descriptiva visible en el reproductor.
        artist: Nombre del artista, intérprete, actor de voz o creador.
        comment: Comentarios contextuales o notas incrustadas.
        encoder: Nombre o versión del software/biblioteca usado para codificar la pista.
        tags: Diccionario para almacenar cualquier otra etiqueta no estandarizada.
    """

    language: str | None = None
    title: str | None = None
    artist: str | None = None
    comment: str | None = None
    encoder: str | None = None
    tags: dict[str, str] = field(default_factory=dict)


@dataclass(kw_only=True)
class AudioDispositions:
    """Banderas operativas de comportamiento de la pista.

    Attributes:
        default: Si es la pista de audio por defecto a reproducir en el contenedor.
        forced: Si es una pista de reproducción forzada por el contenedor.
        hearing_impaired: Si pista adaptada para personas con discapacidad auditiva.
        commentary: Si contiene comentarios del director, equipo o audio adicional.
        dubbed: Si es una pista doblada a otro idioma diferente al original.
        original: Si es la pista en su idioma original de producción.
        lyrics: Si la pista incluye o representa contenido de letras de canciones.
        karaoke: Si es una pista destinada a uso de karaoke (sin voz principal).
        visual_impaired: Si audiodescripción para personas con discapacidad visual.
        clean_effects: Si únicamente efectos de sonido limpios (sin diálogos ni música).
    """

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
    """Información completa de una pista de audio.

    Attributes:
        path: Ruta del archivo fuente o contenedor del audio.
        global_index: Índice global del flujo (stream) dentro del contenedor multimedia.
        track_index: Índice relativo dentro del listado exclusivo de pistas de audio.
        duration: Duración total de la pista de audio.
        format: Objeto con los parámetros del formato técnico y codificación.
        loudness: Objeto con las métricas de volumen y normalización de sonoridad.
        metadata: Objeto con las etiquetas de metadatos descriptivos.
        dispositions: Objeto con las banderas operativas de comportamiento.
    """

    path: Path
    global_index: int | None = None
    track_index: int | None = None
    duration: timedelta | None = None

    format: AudioFormat = field(default_factory=AudioFormat)
    loudness: AudioLoudness = field(default_factory=AudioLoudness)
    metadata: AudioMetadata = field(default_factory=AudioMetadata)
    dispositions: AudioDispositions = field(default_factory=AudioDispositions)
