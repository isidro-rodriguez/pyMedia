"""Información y metadatos de una pista de subtítulos."""

from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path


@dataclass(kw_only=True)
class SubtitlesFormat:
    """Propiedades técnicas del formato y codificación de la pista de subtítulos.

    Attributes:
        codec: Nombre del códec de subtítulos en ffprobe (p. ej. "subrip", "ass").
        mimetype: Tipo MIME del formato de subtítulo si está definido en el contenedor.
        is_text_based: Indica si el subtítulo es basado en texto plano/estilos
            (SRT, ASS) o en mapas de bits (PGS, VobSub).
    """

    codec: str | None = None
    mimetype: str | None = None
    is_text_based: bool | None = None


@dataclass(kw_only=True)
class SubtitlesMetadata:
    """Etiquetas de metadatos descriptivos (clave-valor) de la pista de subtítulos.

    Attributes:
        language: Código del idioma de la pista (p. ej. "spa", "eng", "zxx").
        title: Título o etiqueta descriptiva visible en el reproductor.
        encoder: Nombre o versión del software usado para generar o codificar la pista.
        tags: Diccionario para almacenar cualquier otra etiqueta no estandarizada.
    """

    language: str | None = None
    title: str | None = None
    encoder: str | None = None
    tags: dict[str, str] = field(default_factory=dict)


@dataclass(kw_only=True)
class SubtitlesDispositions:
    """Banderas operativas de comportamiento de la pista de subtítulos.

    Attributes:
        default: Si es la pista de subtítulos por defecto a reproducir en el contenedor.
        forced: Si es una pista de subtítulos de reproducción forzada.
        hearing_impaired: Si subtítulos adaptados para discapacidad auditiva (SDH / CC).
        visual_impaired: Si son subtítulos orientados a descripción o apoyo visual.
        original: Si la pista de subtítulos está en el idioma original de la obra.
        dub: Si la pista de subtítulos corresponde a la versión doblada.
        commentary: Si la pista contiene comentarios del director o del equipo técnico.
        lyrics: Si la pista contiene únicamente la letra de las canciones.
        karaoke: Si es una pista destinada a sincronización tipo karaoke.
        captions: Si contiene Closed Captions formateados.
        descriptions: Si la pista contiene descripciones del contenido visual.
        metadata: Si contiene metadatos sincronizados en lugar de texto visible.
    """

    default: bool | None = None
    forced: bool | None = None
    hearing_impaired: bool | None = None
    visual_impaired: bool | None = None
    original: bool | None = None
    dub: bool | None = None
    commentary: bool | None = None
    lyrics: bool | None = None
    karaoke: bool | None = None
    captions: bool | None = None
    descriptions: bool | None = None
    metadata: bool | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class Subtitles:
    """Información completa de una pista de subtítulos.

    Attributes:
        path: Ruta del archivo fuente o contenedor del subtítulo.
        global_index: Índice global del flujo (stream) dentro del contenedor multimedia.
        track_index: Índice relativo dentro del listado de pistas de subtítulos.
        duration: Duración total de la pista de subtítulos si está especificada.
        format: Objeto con los parámetros del formato técnico y codificación.
        metadata: Objeto con las etiquetas de metadatos descriptivos.
        dispositions: Objeto con las banderas operativas de comportamiento.
    """

    path: Path
    global_index: int | None = None
    track_index: int | None = None
    duration: timedelta | None = None

    format: SubtitlesFormat = field(default_factory=SubtitlesFormat)
    metadata: SubtitlesMetadata = field(default_factory=SubtitlesMetadata)
    dispositions: SubtitlesDispositions = field(default_factory=SubtitlesDispositions)
