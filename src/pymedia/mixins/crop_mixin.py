"""Mixin de recorte de imagen (filtro crop de ffmpeg)."""

from dataclasses import dataclass
from pathlib import Path

from pymedia.errors import (
    MissingParameterError,
    MissingPropertyError,
    UserError,
)
from pymedia.locales import _  # noqa
from pymedia.models.media import Media
from pymedia.types import CropArea


@dataclass(kw_only=True)
class CropMixin:
    """Mixin para el recorte de imagen.

    Attributes:
        crop_area: Área y coordenada de la zona a preservar de la imagen.
    """

    media: Media | None = None
    media_output: Path | None = None
    crop_area: CropArea | None = None

    def create_crop(self, crop_str: str | None) -> None:
        """Crea el atributo crop, parseando y validando la opción del usuario.

        Args:
            crop_str: String con el valor de crop indicado por el usuario.

        Raises:
            InvalidArgumentError: Si el formato del string de crop no es
                válido.
            InvalidParameterError: Si el valor del parámetro no es válido.
            MissingPropertyError: Si no se ha obtenido un parámetro importante.
        """
        if crop_str is None:
            return
        if self.media is None:
            raise MissingParameterError(name="media")
        self.crop_area = self._process_crop_area(crop_str=crop_str, media=self.media)

    def to_crop_cmd(self) -> str:
        """Devuelve el filtro listo para consumo de ffmpeg.

        Returns:
            El filtro `crop=W:H:X:Y` listo para ffmpeg.

        Raises:
            MissingParameterError: Si no se ha obtenido un parámetro importante.
        """
        if self.crop_area is None:
            raise MissingParameterError(name="crop")
        crop = self.crop_area

        #
        if self.media_output is not None:
            return f"crop={crop.width}:{crop.height}:{crop.x}:{crop.y}"
        else:
            return f"crop={crop.width}:{crop.height}:{crop.x}:{crop.y}:exact=1"

    @staticmethod
    def _process_crop_area(crop_str: str, media: Media) -> CropArea:
        """Procesa el string del argumento crop del usuario."""

        def _parse_crop_area() -> CropArea:
            """Parsea el valor de crop del usuario y lo convierte en enteros."""
            try:
                width_str, height_str, x_str, y_str = crop_str.split(",")
                width, height, x, y = (
                    int(width_str),
                    int(height_str),
                    int(x_str),
                    int(y_str),
                )
            except ValueError as err:
                raise UserError(
                    msg=_("Invalid crop %(crop_str)s. Expected: WIDTH,HEIGHT,X,Y")
                    % {"crop_str": crop_str}
                ) from err
            return CropArea(width=width, height=height, x=x, y=y)

        def _validate_crop_area() -> None:
            """Comprueba que los valores aportados puedan resultar en un crop válido."""
            video = media.video
            if video is None or video.width is None or video.height is None:
                raise MissingPropertyError(name="video")

            if crop_area.width == 0 or crop_area.height == 0:
                raise UserError(
                    msg=_(
                        "Invalid crop dimensions: width and height must be "
                        "greater than 0."
                    )
                )

            if crop_area.width + crop_area.x >= video.width:
                raise UserError(
                    msg=_(
                        "Invalid crop area. Area width (%(area_width)s) and coordinate "
                        "X (%(area_x)s) is bigger than video width (%(video_width)s) "
                    )
                    % {
                        "area_width": crop_area.width,
                        "area_x": crop_area.x,
                        "video_width": video.width,
                    }
                )

            if crop_area.height + crop_area.y > video.height:
                raise UserError(
                    msg=_(
                        "Invalid crop area. Area height (%(area_height)s) and "
                        "coordinate Y (%(area_y)s) is bigger than video height "
                        "(%(video_height)s) "
                    )
                    % {
                        "area_height": crop_area.height,
                        "area_y": crop_area.y,
                        "video_height": video.height,
                    }
                )

        crop_area: CropArea = _parse_crop_area()
        _validate_crop_area()
        return crop_area
