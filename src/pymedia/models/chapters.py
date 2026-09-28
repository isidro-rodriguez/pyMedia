"""Información y metadatos de capítulos en un contenedor multimedia."""

from dataclasses import dataclass, field
from datetime import timedelta


@dataclass(kw_only=True, frozen=True, slots=True)
class ChapterFormat:
    """Propiedades técnicas de sincronización y base temporal del capítulo.

    Attributes:
        time_base: Escala de tiempo usada por el contenedor.
        start: Tiempo de inicio del capítulo expresado en unidades de time_base.
        end: Tiempo de fin del capítulo expresado en unidades de time_base.
    """

    time_base: str | None = None
    start: timedelta | None = None
    end: timedelta | None = None


@dataclass(kw_only=True)
class ChapterMetadata:
    """Etiquetas descriptivas asociadas al capítulo.

    Attributes:
        title: Título visible del (p. ej. "Escena 3: La Persecución").
        tags: Diccionario para almacenar cualquier otra etiqueta no estandarizada.
    """

    title: str | None = None
    tags: dict[str, str] = field(default_factory=dict)


@dataclass(kw_only=True, frozen=True, slots=True)
class Chapter:
    """Información completa de un capítulo individual del contenedor.

    Attributes:
        id: Identificador único del capítulo asignado por el contenedor.
        start_time: Punto temporal de inicio del capítulo.
        end_time: Punto temporal de finalización del capítulo.
        format: Objeto con la información técnica de escala temporal.
        metadata: Objeto con el título y etiquetas descriptivas.
    """

    id: int | None = None
    start_time: timedelta | None = None
    end_time: timedelta | None = None

    format: ChapterFormat = field(default_factory=ChapterFormat)
    metadata: ChapterMetadata = field(default_factory=ChapterMetadata)
