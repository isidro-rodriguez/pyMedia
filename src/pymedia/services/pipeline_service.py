from datetime import timedelta
from pathlib import Path

from pymedia.cli_params import GyrateMode, ScaleGifMode, ScaleMode
from pymedia.feedback.errors import (
    CropAllZeroError,
    CropExceedsHeightError,
    CropExceedsWidthError,
    InvalidCropFormatError,
    InvalidGyrateError,
    InvalidTimeFormatError,
    InvalidTrimPointsError,
    MissingMediaError,
    MissingMediaPropertyError,
    NegativeTimeError,
    TimeExceedsDurationError,
)
from pymedia.feedback.logger import get_logger, log_warning
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
        raise InvalidCropFormatError()

    left, right, top, bottom = parsed

    if all([left == 0, right == 0, top == 0, bottom == 0]):
        raise CropAllZeroError()

    for i, media_item in enumerate(media):
        if (
            media_item.video is None
            or media_item.video.width is None
            or media_item.video.height is None
        ):
            raise MissingMediaPropertyError(property_name="Crop")

        if dimensions is not None:
            width, height = dimensions[i]
        else:
            width, height = media_item.video.width, media_item.video.height

        if (left + right) >= width:
            raise CropExceedsWidthError(total=left + right, width=width)

        if (top + bottom) >= height:
            raise CropExceedsHeightError(total=top + bottom, height=height)

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
            raise InvalidGyrateError()


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
                property_name="resolución del vídeo para validar el escalado"
            )

        if scale == media_item.video.height:
            log_warning(
                logger,
                "scale_rejected_equal",
                scale=scale,
                height=media_item.video.height,
            )
            scale_list.append(None)
            continue

        if reject_increase and scale.value > media_item.video.height:
            log_warning(
                logger,
                "scale_rejected_increase",
                scale=scale.value,
                height=media_item.video.height,
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
        raise InvalidTimeFormatError()

    if time_delta < timedelta(0):
        raise NegativeTimeError()

    if video_duration is None:
        raise MissingMediaPropertyError(
            property_name="duración del vídeo para validar la marca de tiempo"
        )

    if time_delta > video_duration:
        raise TimeExceedsDurationError(time=time_delta, duration=video_duration)

    return time_delta.total_seconds()


def process_trim_points(
    trim_points: str,
    video_duration: timedelta | None,
    input_path: Path,
) -> str:
    """Valida y procesa los puntos de corte."""
    if video_duration is None:
        raise MissingMediaError(path=input_path)

    times_timedelta: list[timedelta] = []

    for tp in trim_points.split(","):
        t = convert_to_timedelta(tp)
        if t is None:
            raise InvalidTimeFormatError()
        if t > video_duration:
            raise InvalidTrimPointsError()
        times_timedelta.append(t)

    return ",".join(str(t.total_seconds()) for t in times_timedelta)
