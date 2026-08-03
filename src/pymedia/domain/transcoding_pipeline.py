from dataclasses import dataclass

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
        gyrate: int | None = None,
        remux: bool = False,
        scale: int | None = None,
    ) -> "TranscodingPipeline":
        return cls(crop=crop, gyrate=gyrate, remux=remux, scale=scale)

    def validate(self, media: MediaInput) -> None:
        if self.crop:
            crop = parse_crop(self.crop)
            if crop is None:
                raise ValueError(
                    "Formato de crop inválido. Esperado: IZQ,DER,ARRIBA,ABAJO"
                )
            if not self._validate_crop(media):
                raise ValueError("Valores de corte mayores a las resolución del vídeo")

        if self.scale:
            if not self._validate_scale(media):
                raise ValueError("Altura de escala mayor a la del vídeo original")

    def _validate_crop(self, media: MediaInput) -> bool:
        parsed = parse_crop(self.crop)
        if parsed is None or media.video is None:
            return False
        if (parsed[0] + parsed[1]) > media.video.width:
            return False
        if (parsed[2] + parsed[3]) > media.video.height:
            return False
        return True

    def _validate_scale(self, media: MediaInput) -> bool:
        if media.video is None:
            return False
        if media.video.height is None:
            return False
        if self.scale is None:
            return False
        if self.scale >= media.video.height:
            print(f"{self.scale} >= {media.video.height}")
            return False
        return True
