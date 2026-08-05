from dataclasses import dataclass

from pymedia.cli_params import GyrateMode, ScaleGifMode, ScaleMode
from pymedia.domain.errors import (
    InvalidCropFormatError,
    InvalidScaleError,
    NoVideoStreamError,
)
from pymedia.domain.media_input import MediaInput
from pymedia.logger import get_logger
from pymedia.utils import parse_crop

logger = get_logger("pipeline")


@dataclass
class EncodePipeline:
    crop: str | None = None
    gyrate: int | None = None
    remux: bool = False
    scale: int | None = None

    @classmethod
    def load(
        cls,
        crop: str | None = None,
        gyrate: GyrateMode | None = None,
        remux: bool = False,
        scale: ScaleMode | ScaleGifMode | None = None,
    ) -> "EncodePipeline":
        """Crea un pipeline desde los parámetros CLI, convirtiendo enums a sus valores."""
        if gyrate is not None:
            gyrate = gyrate.value
        if scale is not None:
            scale = scale.value
        return cls(crop=crop, gyrate=gyrate, remux=remux, scale=scale)

    @property
    def has_operations(self) -> bool:
        """True si hay al menos una operación activa en el pipeline."""
        return any(
            field is not None for field in (self.crop, self.gyrate, self.scale)
        ) or self.remux

    def validate(self, media: MediaInput) -> None:
        """Valida el pipeline contra el medio, descartando operaciones inválidas.

        Mutates the pipeline in place: sets invalid fields to ``None``.
        """
        if self.crop is not None:
            self._validate_crop(media)

        if self.scale is not None:
            self._validate_scale(media)

    def _validate_crop(self, media: MediaInput) -> None:
        if media.video is None:
            logger.warning(
                "Crop ignorado: no se encontró stream de vídeo en el archivo."
            )
            self.crop = None
            return

        if media.video.width is None or media.video.height is None:
            raise InvalidCropFormatError(
                "No se pudo obtener la resolución del vídeo para validar el crop."
            )

        parsed = parse_crop(self.crop)
        if parsed is None:
            raise InvalidCropFormatError(
                "Formato de crop inválido. Esperado: IZQ,DER,ARRIBA,ABAJO"
            )

        left, right, top, bottom = parsed

        if (left + right) >= media.video.width:
            logger.warning(
                "Crop ignorado: %s >= ancho original (%s).",
                left + right,
                media.video.width,
            )
            self.crop = None
            return

        if (top + bottom) >= media.video.height:
            logger.warning(
                "Crop ignorado: %s >= alto original (%s).",
                top + bottom,
                media.video.height,
            )
            self.crop = None

    def _validate_scale(self, media: MediaInput) -> None:
        if media.video is None:
            raise NoVideoStreamError("No se encontró stream de vídeo en el archivo.")

        if media.video.height is None:
            raise InvalidScaleError("No se pudo obtener la altura del vídeo.")

        if self.scale >= media.video.height:
            logger.warning(
                "Escala ignorada: %s >= altura original (%s).",
                self.scale,
                media.video.height,
            )
            self.scale = None
