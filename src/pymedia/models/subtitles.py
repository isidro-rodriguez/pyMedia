"""Información de una pista de subtítulos."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(kw_only=True)
class SubtitlesMetadata:
    """Metadatos de pista de subtítulos.

    Attributes:
        language: Código de idioma de la pista.
        title: Título descriptivo de la pista.
    """

    language: str | None = None
    title: str | None = None


@dataclass(kw_only=True)
class SubtitlesDispositions:
    """Disposiciones de pista de subtítulos.

    Attributes:
        forced: Si la pista está marcada como forzada.
        default: Si la pista está marcada como predeterminada.
        original: Si la pista contiene el idioma original.
        dub: Si la pista corresponde a contenido doblado.
        comment: Si la pista contiene comentarios.
        lyrics: Si la pista contiene letras de canciones.
        karaoke: Si la pista es de tipo karaoke.
        hearing_impaired: Si son subtítulos para personas con problemas auditivos.
        visual_impaired: Si son subtítulos para personas con problemas visuales.
        captions: Si la pista contiene captions.
        descriptions: Si la pista contiene descripciones del contenido visual.
        metadata: Si la pista contiene metadatos sincronizados temporalmente.
    """

    forced: bool | None = None
    default: bool | None = None
    original: bool | None = None
    dub: bool | None = None
    comment: bool | None = None
    lyrics: bool | None = None
    karaoke: bool | None = None
    hearing_impaired: bool | None = None
    visual_impaired: bool | None = None
    captions: bool | None = None
    descriptions: bool | None = None
    metadata: bool | None = None


@dataclass(kw_only=True, frozen=True, slots=True)
class Subtitles:
    """Información de pista de subtítulos.

    Attributes:
        path: Ruta absoluta al fichero de subtítulos.
        global_index: Índice de la pista dentro del contenedor.
        track_index: Índice de la pista en el listado de subtítulos.
        codec: Nombre del códec de subtítulos.
        dispositions: Disposiciones de la pista de subtítulos.
    """

    path: Path
    global_index: int | None = None
    track_index: int | None = None
    codec: str | None = None
    metadata: SubtitlesMetadata = field(default_factory=SubtitlesMetadata)
    dispositions: SubtitlesDispositions = field(default_factory=SubtitlesDispositions)
