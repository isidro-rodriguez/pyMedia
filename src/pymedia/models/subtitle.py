"""Metadatos de una pista de subtítulos."""

from dataclasses import dataclass
from pathlib import Path

from pymedia.locales import _  # noqa


@dataclass(frozen=True, kw_only=True, slots=True)
class Subtitle:
    """Metadatos de una pista de subtítulos de un medio.

    Attributes:
        index: Índice de la pista dentro del contenedor.
        codec: Nombre del códec de subtítulos.
        language: Código de idioma de la pista.
        title: Título descriptivo de la pista.
        forced: Si la pista está marcada como forzada.
        default: Si la pista está marcada como predeterminada.
        hearing_impaired: Si son subtítulos para personas con problemas auditivos.
        visual_impaired: Si son subtítulos para personas con problemas visuales.
    """

    path: Path
    index: int | None = None
    codec: str | None = None
    language: str | None = None
    title: str | None = None
    forced: bool = False
    default: bool = False
    hearing_impaired: bool = False
    visual_impaired: bool = False
