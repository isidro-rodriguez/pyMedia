from dataclasses import dataclass


@dataclass(frozen=True)
class ImageFormatData:
    """Configuración e información técnica de un formato de imagen estática.

    Esta clase inmutable almacena los parámetros necesarios para la
    extracción de fotogramas y conversión de imágenes con FFmpeg.

    Attributes:
        name: Nombre identificador del formato (p. ej., 'jpeg', 'png').
        codec: Nombre del códec utilizado por FFmpeg para procesar la imagen (p.
            ej., 'mjpeg', 'png', 'libwebp').
        extension: Extensión de archivo asociada incluyendo el punto (p. ej.,
            '.jpg', '.png').
        supports_lossless: Indica si el formato admite compresión sin pérdidas (p.
            ej., True para PNG/WebP, False para JPEG).
        default_pix_fmt: Formato de píxeles predeterminado utilizado por FFmpeg
            para este formato (p. ej., 'yuvj420p', 'rgb24').
    """

    name: str
    codec: str
    extension: str
    supports_lossless: bool
    default_pix_fmt: str


IMAGE_FORMATS = {
    "jpeg": ImageFormatData(
        name="jpeg",
        codec="mjpeg",
        extension=".jpg",
        supports_lossless=False,
        default_pix_fmt="yuvj420p",
    ),
    "png": ImageFormatData(
        name="png",
        codec="png",
        extension=".png",
        supports_lossless=True,
        default_pix_fmt="rgb24",
    ),
    "webp": ImageFormatData(
        name="webp",
        codec="libwebp",
        extension=".webp",
        supports_lossless=True,
        default_pix_fmt="yuv420p",
    ),
}
