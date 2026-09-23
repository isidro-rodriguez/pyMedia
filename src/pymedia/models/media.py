"""Modelos de metadatos de medios obtenidos mediante ffprobe."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from pymedia.models.audio import Audio
from pymedia.models.subtitles import Subtitles
from pymedia.models.video import Video


@dataclass(frozen=True, kw_only=True, slots=True)
class MediaMetadata:
    """Metadatos globales del contenedor obtenidos mediante ffprobe.

    Estos metadatos se aplican al fichero multimedia completo y no a una
    pista concreta de vídeo, audio o subtítulos. Los valores disponibles
    dependen del contenedor y del contenido original.

    Attributes:
        title: Título del contenido o del contenedor.
        comment: Comentario asociado al contenido.
        description: Descripción del contenido.
        synopsis: Sinopsis o resumen breve del contenido.
        genre: Género o categoría del contenido.
        date: Fecha del contenido, con hora y zona ignoradas al parsearla.
        copyright: Información de copyright o licencia del contenido.
        law_rating: Clasificación por edad o calificación legal del contenido.
        artist: Autor, creador o artista asociado al contenido.
        album: Álbum al que pertenece el contenido.
        encoder: Aplicación o biblioteca que generó el contenedor.
    """

    title: str | None = None
    comment: str | None = None
    description: str | None = None
    synopsis: str | None = None
    genre: str | None = None
    date: datetime | None = None
    copyright: str | None = None
    law_rating: str | None = None
    artist: str | None = None
    album: str | None = None
    encoder: str | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class Media:
    """Información del contenedor obtenida mediante ffprobe.

    Attributes:
        path: Ruta absoluta del fichero de media a procesar.
        duration: Duración total del medio.
        size: Tamaño del fichero en bytes.
        format_name: Nombre del formato contenedor.
        video: Metadatos de la pista de vídeo, o None si no existe.
        audio: Lista de pistas de audio, o None si no hay.
        subtitles: Lista de pistas de subtítulos, o None si no hay.
    """

    path: Path
    duration: timedelta | None = None
    size: int | None = None
    format_name: str | None = None
    video: Video | None = None
    audio: list[Audio] | None = None
    subtitles: list[Subtitles] | None = None
    metadata: MediaMetadata | None = None
