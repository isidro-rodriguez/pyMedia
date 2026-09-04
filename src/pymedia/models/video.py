"""Metadatos de una pista de vídeo."""

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True, kw_only=True, slots=True)
class Video:
    """Metadatos de la pista de vídeo de un medio.

    Attributes:
        codec: Nombre del códec de vídeo.
        width: Ancho en píxeles.
        height: Alto en píxeles.
        fps: Frecuencia de imágenes por segundo.
        bit_rate: Tasa de bits en bps.
        pix_fmt: Formato de píxeles.
        aspect_ratio: Relación de aspecto mostrada.
        profile: Perfil del códec.
    """

    codec: str | None = None
    width: int | None = None
    height: int | None = None
    fps: Fraction | None = None
    bit_rate: int | None = None
    pix_fmt: str | None = None
    aspect_ratio: str | None = None
    profile: str | None = None
