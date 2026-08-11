from datetime import timedelta
from pathlib import Path

from pymedia.cli_params import GyrateMode, ScaleGifMode, ScaleMode
from pymedia.logger import get_logger
from pymedia.models.errors import (
    InvalidOptionError,
    MissingMediaError,
    MissingMediaPropertyError,
)
from pymedia.models.media import Media
from pymedia.utils import convert_to_timedelta, parse_crop

logger = get_logger("pipeline")


def process_crop(
    crop: str | None,
    media: list[Media],
    dimensions: list[tuple[int, int]] | None = None,
) -> list[str]:
    """Valida y procesa la opción de corte.

    Si `dimensions` se proporciona, se usan esas dimensiones (ancho, alto)
    en lugar de las del vídeo original. Útil para concat, donde los vídeos
    se escalan a una resolución objetivo antes de recortar.
    """
    crop_list: list[str] = []

    parsed = parse_crop(crop)

    if parsed is None:
        raise InvalidOptionError(
            "Formato de crop inválido. Esperado: IZQ,DER,ARRIBA,ABAJO"
        )

    left, right, top, bottom = parsed

    if all([left == 0, right == 0, top == 0, bottom == 0]):
        raise InvalidOptionError("Crop inválido. Todos los valores son 0.")

    for i, media_item in enumerate(media):
        if (
            media_item.video is None
            or media_item.video.width is None
            or media_item.video.height is None
        ):
            raise MissingMediaPropertyError("Crop")

        if dimensions is not None:
            width, height = dimensions[i]
        else:
            width, height = media_item.video.width, media_item.video.height

        if (left + right) >= width:
            raise InvalidOptionError(
                f"Crop inválido: {left + right} >= ancho original {width}."
            )

        if (top + bottom) >= height:
            raise InvalidOptionError(
                f"Crop inválido: {top + bottom} >= alto original {height}."
            )

        crop_w = width - left - right
        crop_h = height - top - bottom
        crop_list.append(f"crop={crop_w}:{crop_h}:{left}:{top}")

    return crop_list


def process_gyrate(gyrate: GyrateMode) -> str:
    """Valida y procesa la opción de giro."""
    match gyrate:
        case GyrateMode.d90:
            return "transpose=1"
        case GyrateMode.d180:
            return "vflip,hflip"
        case GyrateMode.d270:
            return "transpose=2"
        case _:
            raise InvalidOptionError(
                "Formato de giro no valido. Esperado 90 | 180 | 270."
            )


def process_scale(
    scale: ScaleMode | ScaleGifMode,
    media: list[Media],
    reject_increase: bool,
) -> list[str | None]:
    """Valida y procesa la opción de escalado."""
    scale_list: list[str | None] = []

    for media_item in media:
        if media_item.video is None or media_item.video.height is None:
            raise MissingMediaPropertyError(
                "No se pudo obtener la resolución del vídeo para validar el escalado."
            )

        if scale == media_item.video.height:
            logger.warning(
                f"Escalado rechazado: {scale} = altura original "
                f"{media_item.video.height}."
            )
            scale_list.append(None)
            continue

        if reject_increase and scale.value > media_item.video.height:
            logger.warning(
                f"Escalado a {scale.value}p no aplicado: resolución mayor "
                f"que la original ({media_item.video.height}p)."
            )
            scale_list.append(None)
            continue

        if reject_increase:
            scale_list.append(f"scale=-2:min({scale.value}\\,ih)")
        else:
            scale_list.append(f"scale=-2:{scale.value}")

    return scale_list


def process_time(time_str: str, video_duration: timedelta | None) -> float:
    """Valida y procesa una marca de tiempo."""
    time_delta = convert_to_timedelta(time_str)

    if time_delta is None:
        raise InvalidOptionError(
            "Formato de marca de tiempo no válida. Esperado hh:mm:ss."
        )

    if time_delta < timedelta(0):
        raise InvalidOptionError("Marca de tiempo negativa.")

    if video_duration is None:
        raise MissingMediaPropertyError(
            "No se pudo obtener la duración del vídeo para validar la marca de tiempo"
        )

    if time_delta > video_duration:
        raise InvalidOptionError(
            f"Marca de tiempo {time_delta} > duración vídeo {video_duration}."
        )

    return time_delta.total_seconds()


def process_trim_points(
    trim_points: str,
    video_duration: timedelta | None,
    input_path: Path,
) -> str:
    """Valida y procesa los puntos de corte."""
    if video_duration is None:
        raise MissingMediaError(input_path)

    times_timedelta: list[timedelta] = []

    for tp in trim_points.split(","):
        t = convert_to_timedelta(tp)
        if t is None:
            raise InvalidOptionError(
                "Formato de marca de tiempo no válida. Esperado hh:mm:ss"
            )
        if t > video_duration:
            raise InvalidOptionError()
        times_timedelta.append(t)

    return ",".join(str(t.total_seconds()) for t in times_timedelta)
