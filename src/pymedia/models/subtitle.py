"""Metadatos de una pista de subtítulos."""

from dataclasses import dataclass


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
    """

    index: int | None = None
    codec: str | None = None
    language: str | None = None
    title: str | None = None
    forced: bool | None = None
    default: bool | None = None
