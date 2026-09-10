"""Mixin de volteo horizontal y vertical de la imagen."""

from dataclasses import dataclass

from pymedia.errors import InvalidParameterError
from pymedia.locales import _  # noqa


@dataclass(kw_only=True)
class FlipMixin:
    """Mixin para invertir la imagen de un vídeo o captura.

    Attributes:
        hflip: Invierte la imagen horizontalmente, intercambia izquierda y derecha.
        vflip: Invierte la imagen verticalmente, intercambiando arriba y abajo.
    """

    hflip: bool = False
    vflip: bool = False

    def to_flip_cmd(self) -> str:
        """Devuelve el filtro listo para consumo de ffmpeg."""
        if self.hflip and self.vflip:
            return "hflip,vflip"
        if self.hflip:
            return "hflip"
        if self.vflip:
            return "vflip"
        raise InvalidParameterError(msg=_("Invalid flip name."))
