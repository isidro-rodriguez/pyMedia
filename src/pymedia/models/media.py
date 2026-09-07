"""Modelos de metadatos de medios obtenidos mediante ffprobe."""

from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path

from pymedia.models.audio import Audio
from pymedia.models.subtitles import Subtitles
from pymedia.models.video import Video


@dataclass(frozen=True, kw_only=True, slots=True)
class Media:
    """Metadatos agregados de un medio obtenidos de ffprobe.

    Attributes:
        path: Ruta absoluta del fichero de media a procesar.
        duration: Duración total del medio.
        size: Tamaño del fichero en bytes.
        format_name: Nombre del formato contenedor.
        video: Metadatos de la pista de vídeo, o None si no existe.
        audio: Lista de pistas de audio, o None si no hay.
        subtitle: Lista de pistas de subtítulos, o None si no hay.
    """

    path: Path
    duration: timedelta | None = None
    size: int | None = None
    format_name: str | None = None
    video: Video | None = None
    audio: list[Audio] | None = None
    subtitle: list[Subtitles] | None = None
