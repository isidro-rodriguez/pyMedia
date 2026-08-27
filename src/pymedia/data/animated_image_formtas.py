from dataclasses import dataclass


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


ANIMATED_IMAGE_FORMATS = {
    "gif": AnimatedImageFormatData(
        name="gif",
        codec="gif",
        extension=".gif",
        supports_transparency=True,
        requires_palette=True,
    ),
    "webp_anim": AnimatedImageFormatData(
        name="webp_anim",
        codec="libwebp",
        extension=".webp",
        supports_transparency=True,
        requires_palette=False,
    ),
    "apng": AnimatedImageFormatData(
        name="apng",
        codec="apng",
        extension=".png",
        supports_transparency=True,
        requires_palette=False,
    ),
}
