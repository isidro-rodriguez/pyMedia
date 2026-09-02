"""Datos estáticos de formatos de imagen animada soportados."""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True)
class AnimatedImageFormatData:
    """Configuración e información técnica de un formato de imagen animada.

    Esta clase inmutable almacena los parámetros necesarios para la
    generación y optimización de secuencias animadas con FFmpeg.

    Attributes:
        name: Nombre identificador del formato animado (p. ej., 'gif',
            'webp_anim', 'apng').
        codec: Nombre del códec utilizado por FFmpeg para procesar la animación
            (p. ej., 'gif', 'libwebp', 'apng').
        extension: Extensión de archivo asociada incluyendo el punto (p. ej.,
            '.gif', '.webp', '.png').
        supports_transparency: Indica si el formato admite canal alfa para
            transparencias en las animaciones.
        requires_palette: Indica si el proceso requiere la generación de una
            paleta de colores optimizada previa (p. ej., filtros palettegen/paletteuse
            en GIF) para evitar pérdida de calidad.
    """

    name: str
    codec: str
    extension: str
    supports_transparency: bool
    requires_palette: bool


_ANIMATED_IMAGE_FORMATS: tuple[AnimatedImageFormatData, ...] = (
    AnimatedImageFormatData(
        name="gif",
        codec="gif",
        extension=".gif",
        supports_transparency=True,
        requires_palette=True,
    ),
    AnimatedImageFormatData(
        name="webp_anim",
        codec="libwebp",
        extension=".webp",
        supports_transparency=True,
        requires_palette=False,
    ),
    AnimatedImageFormatData(
        name="apng",
        codec="apng",
        extension=".png",
        supports_transparency=True,
        requires_palette=False,
    ),
)

ANIMATED_IMAGE_FORMATS: Mapping[str, AnimatedImageFormatData] = MappingProxyType(
    {fmt.name: fmt for fmt in _ANIMATED_IMAGE_FORMATS}
)
"""dict[str, AnimatedImageFormatData]: Imágenes animadas indexadas por nombre."""
