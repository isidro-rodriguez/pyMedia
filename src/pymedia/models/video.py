"""Información y metadatos de una pista de vídeo."""

from dataclasses import dataclass, field
from datetime import timedelta
from fractions import Fraction
from pathlib import Path


@dataclass(kw_only=True)
class VideoFormat:
    """Propiedades técnicas del formato, codificación y renderizado del flujo de vídeo.

    Attributes:
        codec: Nombre del códec de vídeo (p. ej. "h264", "hevc", "av1", "vp9").
        profile: Perfil del códec de vídeo (p. ej. "Main", "High", "Main 10").
        width: Ancho de la imagen en píxeles.
        height: Alto de la imagen en píxeles.
        fps: Frecuencia de imágenes por segundo (Frames Per Second).
        bit_rate: Tasa de bits de la pista en bits por segundo (bps).
        pix_fmt: Formato de píxeles y espacio de color (p. ej. "yuv420p").
        aspect_ratio: Relación de aspecto de visualización (Display Aspect Ratio - DAR).
        pixel_aspect_ratio: Relación de aspecto del píxel (Sample/Pixel Aspect Ratio).
    """

    codec: str | None = None
    profile: str | None = None
    width: int | None = None
    height: int | None = None
    fps: Fraction | None = None
    bit_rate: int | None = None
    pix_fmt: str | None = None
    aspect_ratio: str | None = None
    pixel_aspect_ratio: str | None = None


@dataclass(kw_only=True)
class VideoMetadata:
    """Etiquetas de metadatos descriptivos (clave-valor) de la pista de vídeo.

    Attributes:
        language: Código del idioma asociado a la pista de vídeo si aplica.
        title: Título o etiqueta descriptiva visible en el reproductor.
        encoder: Nombre o versión del software/biblioteca usado para codificar la pista.
        tags: Diccionario para almacenar cualquier otra etiqueta no estandarizada.
    """

    language: str | None = None
    title: str | None = None
    encoder: str | None = None
    tags: dict[str, str] = field(default_factory=dict)


@dataclass(kw_only=True)
class VideoDispositions:
    """Banderas operativas de comportamiento de la pista de vídeo.

    Attributes:
        default: Si es la pista de vídeo por defecto a reproducir en el contenedor.
        forced: Si es una pista de reproducción forzada por el contenedor.
        original: Si es la pista de vídeo original.
        commentary: Si es pista de vídeo secundaria de comentarios o tras de cámaras.
        attached_pic: Si la pista es una imagen adjunta estática (p. ej. carátula).
        captions: Si contiene subtítulos incrustados en la señal de vídeo.
    """

    default: bool | None = None
    forced: bool | None = None
    original: bool | None = None
    commentary: bool | None = None
    attached_pic: bool | None = None
    captions: bool | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class Video:
    """Información completa de una pista de vídeo.

    Attributes:
        path: Ruta del archivo fuente o contenedor del vídeo.
        global_index: Índice global del flujo (stream) dentro del contenedor multimedia.
        track_index: Índice relativo dentro del listado exclusivo de pistas de vídeo.
        duration: Duración total de la pista de vídeo.
        format: Objeto con los parámetros del formato técnico y dimensión de imagen.
        metadata: Objeto con las etiquetas de metadatos descriptivos.
        dispositions: Objeto con las banderas operativas de comportamiento.
    """

    path: Path
    global_index: int | None = None
    track_index: int | None = None
    duration: timedelta | None = None

    format: VideoFormat = field(default_factory=VideoFormat)
    metadata: VideoMetadata = field(default_factory=VideoMetadata)
    dispositions: VideoDispositions = field(default_factory=VideoDispositions)
