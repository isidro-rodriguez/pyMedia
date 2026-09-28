"""Modelos de información y metadatos de medios obtenidos mediante ffprobe."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

from pymedia.models.audio import Audio
from pymedia.models.chapters import Chapter
from pymedia.models.subtitles import Subtitles
from pymedia.models.video import Video


@dataclass(kw_only=True, frozen=True, slots=True)
class MediaFormat:
    """Propiedades técnicas del formato contenedor y archivo multimedia.

    Attributes:
        name: Nombre corto del formato contenedor en ffprobe (p. ej."mov,mp4,mkv,...").
        long_name: Nombre descriptivo completo del formato contenedor.
        size: Tamaño total del archivo en bytes.
        bit_rate: Tasa de bits por segundo aproximada del contenedor.
        probe_score: Puntuación de fiabilidad de ffprobe en detección formato (0-100).
        nb_streams: Número total de pistas (vídeo, audio, subtítulos, ...) contenidos.
        nb_programs: Número de programas en el contenedor.
    """

    name: str | None = None
    long_name: str | None = None
    size: int | None = None
    bit_rate: int | None = None
    probe_score: int | None = None
    nb_streams: int | None = None
    nb_programs: int | None = None


@dataclass(kw_only=True)
class MediaMetadata:
    """Metadatos globales del contenedor descriptivos (etiquetas clave-valor).

    Attributes:
        title: Título del contenido o de la obra multimedia.
        comment: Comentario general asociado al contenedor.
        description: Descripción ampliada del contenido.
        synopsis: Sinopsis o resumen breve de la trama/contenido.
        genre: Género o categoría del contenido (p. ej. "Acción", "Documental").
        date: Fecha de creación o publicación del contenido.
        copyright: Información de derechos de autor o licencia.
        law_rating: Calificación por edad o clasificación legal (p. ej. "PG-13").
        artist: Creador, director, artista o estudio asociado.
        album: Colección, saga o álbum al que pertenece la obra.
        encoder: Aplicación, software o biblioteca que generó el contenedor multimedia.
        tags: Diccionario para almacenar cualquier otra etiqueta no estandarizada.
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
    tags: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, kw_only=True, slots=True)
class Media:
    """Información completa del archivo multimedia contenedor.

    Attributes:
        path: Ruta absoluta o relativa al fichero multimedia procesado.
        duration: Duración total estimada del contenedor multimedia.
        format: Objeto con los detalles y propiedades técnicas del formato contenedor.
        metadata: Objeto con las etiquetas de metadatos globales del contenedor.
        video: Pista de vídeo principal.
        audio: Lista de pistas de audio disponibles en el contenedor.
        subtitles: Lista de pistas de subtítulos disponibles en el contenedor.
        chapters: Lista de capítulos definidos en el contenedor, si existen.
    """

    path: Path
    duration: timedelta | None = None

    format: MediaFormat = field(default_factory=MediaFormat)
    metadata: MediaMetadata = field(default_factory=MediaMetadata)

    video: Video | None = None
    audio: list[Audio] | None = field(default_factory=list)
    subtitles: list[Subtitles] | None = field(default_factory=list)
    chapters: list[Chapter] | None = field(default_factory=list)
