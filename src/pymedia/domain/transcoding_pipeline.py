from dataclasses import dataclass

from pymedia.cli_params import GyrateMode, ScaleMode
from pymedia.domain.media_input import MediaInput
from pymedia.utils import parse_crop


@dataclass
class TranscodingPipeline:
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
        scale: ScaleMode | None = None,
    ) -> "TranscodingPipeline":
        if gyrate is not None:
            gyrate = gyrate.value
        if scale is not None:
            scale = scale.value
        return cls(crop=crop, gyrate=gyrate, remux=remux, scale=scale)

    def validate(self, media: MediaInput) -> None:
        if self.crop is not None:
            self._validate_crop(media)

        if self.scale is not None:
            self._validate_scale(media)

    def _validate_crop(self, media: MediaInput) -> None:
        if media.video is None:
            raise ValueError("No se encontró stream de vídeo en el archivo.")

        parsed = parse_crop(self.crop)
        if parsed is None:
            raise ValueError("Formato de crop inválido. Esperado: IZQ,DER,ARRIBA,ABAJO")

        left, right, top, bottom = parsed

        if (left + right) > media.video.width:
            raise ValueError("Valores de corte mayores a la resolución del vídeo.")

        if (top + bottom) > media.video.height:
            raise ValueError("Valores de corte mayores a la resolución del vídeo.")

    def _validate_scale(self, media: MediaInput) -> None:
        if media.video is None:
            raise ValueError("No se encontró stream de vídeo en el archivo.")

        if media.video.height is None:
            raise ValueError("No se pudo obtener la altura del vídeo.")

        if self.scale is None:
            raise ValueError("Valor de escala inválido.")

        if self.scale >= media.video.height:
            raise ValueError(
                "La altura de escala es mayor o igual a la del vídeo original."
            )
