"""Metadatos de una pista de subtítulos."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, kw_only=True, slots=True)
class Subtitles:
    """Metadatos de una pista de subtítulos de un medio.

    Attributes:
        path: Ruta absoluta al fichero de subtítulos.
        global_index: Índice de la pista dentro del contenedor.
        track_index: Índice de la pista en el listado de subtítulos.
        codec: Nombre del códec de subtítulos.
        language: Código de idioma de la pista.
        title: Título descriptivo de la pista.
        forced: Si la pista está marcada como forzada.
        default: Si la pista está marcada como predeterminada.
        hearing_impaired: Si son subtítulos para personas con problemas auditivos.
        visual_impaired: Si son subtítulos para personas con problemas visuales.
    """

    path: Path
    global_index: int | None = None
    track_index: int | None = None
    codec: str | None = None
    language: str | None = None
    title: str | None = None
    forced: bool | None = None
    default: bool | None = None
    hearing_impaired: bool | None = None
    visual_impaired: bool | None = None
