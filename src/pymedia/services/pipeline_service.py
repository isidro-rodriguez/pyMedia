from datetime import timedelta

from pymedia.logger import get_logger
from pymedia.models.errors import (
    InvalidOptionError,
    MissingMediaError,
    MissingMediaPropertyError,
    MissingOptionsError,
)
from pymedia.models.state import State
from pymedia.utils import convert_to_timedelta, parse_crop

logger = get_logger("pipeline")


def process_crop(state: State) -> list[str]:
    """Valida y procesa la opción de corte."""
    crop_list: list[str] = []

    if state.arguments is None or state.arguments.crop is None:
        raise MissingOptionsError("No se pudo obtener los valores de corte.")

    parsed = parse_crop(state.arguments.crop)

    if parsed is None:
        raise InvalidOptionError(
            "Formato de crop inválido. Esperado: IZQ,DER,ARRIBA,ABAJO"
        )

    left, right, top, bottom = parsed

    for media in state.media:
        if (
            media.video is None
            or media.video.width is None
            or media.video.height is None
        ):
            raise MissingMediaPropertyError("Crop")

        if (left + right) >= media.video.width:
            raise InvalidOptionError(
                f"Crop inválido: {left + right} >= ancho original {media.video.width}."
            )

        if (top + bottom) >= media.video.width:
            raise InvalidOptionError(
                f"Crop inválido: {top + bottom} >= ancho original {media.video.height}."
            )

        crop_w = media.video.width - left - right
        crop_h = media.video.height - top - bottom
        crop_list.append(f"crop={crop_w}:{crop_h}:{left}:{top}")

    return crop_list


def process_gyrate(state: State) -> str:
    """Valida y procesa la opción de giro."""
    if state.arguments is None or state.arguments.gyrate is None:
        raise MissingOptionsError("No se pudo obtener el valor de giro.")

    match state.arguments.gyrate:
        case 90:
            return "transpose=1"
        case 180:
            return "vflip,hflip"
        case 270:
            return "transpose=2"
        case _:
            raise InvalidOptionError(
                "Formato de giro no valido. Esperado 90 | 180 | 270."
            )


def process_scale(state: State) -> list[int | None]:
    """Valida y procesa la opción de escalado."""
    if state.arguments is None or state.arguments.scale is None:
        raise MissingOptionsError("No se pudo obtener el valor de escalado")

    scale_list: list[int | None] = []
    scale = state.arguments.scale
    reject_increase = state.config.app.disable_resolution_increase

    for media in state.media:
        if media.video is None or media.video.height is None:
            raise MissingMediaPropertyError(
                "No se pudo obtener la resolución del vídeo para validar el escalado."
            )

        if scale == media.video.height:
            logger.warning(
                f"Escalado rechazado: {scale} = altura original {media.video.height}."
            )
            scale_list.append(None)
            continue

        if reject_increase and scale > media.video.height:
            logger.warning(
                f"Escalado rechazado: {scale} > altura original {media.video.height}."
            )
            scale_list.append(None)
            continue

        scale_list.append(scale)

    return scale_list


def process_time(state: State, time_str: str) -> float:
    """Valida y procesa una marca de tiempo."""
    if not state.media:
        raise MissingMediaError()

    time_delta = convert_to_timedelta(time_str)

    if time_delta is None:
        raise InvalidOptionError(
            "Formato de marca de tiempo no válida. Esperado hh:mm:ss."
        )

    if time_delta < timedelta(0):
        raise InvalidOptionError("Marca de tiempo negativa.")

    video_duration = state.media[0].duration

    if video_duration is None:
        raise MissingMediaPropertyError(
            "No se pudo obtener la duración del vídeo para validar la marca de tiempo"
        )

    if time_delta > video_duration:
        raise InvalidOptionError(
            f"Marca de tiempo {time_delta} > duración vídeo {video_duration}."
        )

    return time_delta.total_seconds()


def process_trim_points(state: State) -> str:
    """Valida y procesa los puntos de corte."""
    if not state.media:
        raise MissingMediaError(state.inputs[0])

    times_timedelta: list[timedelta] = []

    for tp in state.arguments.trim_points.split(","):
        t = convert_to_timedelta(tp)
        if t is None:
            raise InvalidOptionError(
                "Formato de marca de tiempo no válida. Esperado hh:mm:ss"
            )
        if t > state.media[0].duration:
            raise InvalidOptionError()
        times_timedelta.append(t)

    return ",".join(str(t.total_seconds()) for t in times_timedelta)
