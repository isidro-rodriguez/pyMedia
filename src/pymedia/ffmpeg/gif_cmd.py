from pathlib import Path

from pymedia.domain.media import Media
from pymedia.domain.pipeline import Pipeline
from pymedia.logger import get_logger
from pymedia.utils import convert_to_timedelta, parse_crop

logger = get_logger("gif")


def _build_filters(
    media: Media,
    fps: int,
    pipeline: Pipeline,
) -> str:
    encode_filters = []

    if pipeline.crop:
        if media.video is None:
            raise ValueError("Vídeo no encontrado en encode")

        parsed = parse_crop(pipeline.crop)

        if parsed is None:
            raise ValueError("Crop no encontrado en encode")

        left, right, top, bottom = parsed

        crop_w = media.video.width - left - right
        crop_h = media.video.height - top - bottom

        encode_filters.append(f"crop={crop_w}:{crop_h}:{left}:{top}")
    if pipeline.gyrate:
        match pipeline.gyrate:
            case 90:
                encode_filters.append("transpose=1")
            case 180:
                encode_filters.append("vflip,hflip")
            case 270:
                encode_filters.append("transpose=2")
    if pipeline.scale:
        # int(scale) resuelve enums tipo ScaleGifMode(int, Enum) a su valor numérico
        encode_filters.append(f"scale=-2:{int(pipeline.scale)}:flags=lanczos")

    filters = ",".join(encode_filters)
    if filters:
        filters += ","

    filters += (
        f"fps={fps},split[a][b];[a]palettegen[p];"
        f"[b][p]paletteuse=dither=floyd_steinberg"
    )

    return filters


def gif_cmd(
    path: Path,
    pipeline: Pipeline,
    media: Media,
    fps: int | None = None,
    start_point: str | None = None,
    end_point: str | None = None,
    output_name: str | None = None,
) -> list[str]:

    if fps is None:
        logger.error("Recepción de FPS inválida.")
        exit(1)

    filters: str = _build_filters(media, fps, pipeline)

    if output_name:
        output = output_name if output_name.endswith(".gif") else output_name + ".gif"
    else:
        output = path.stem + ".gif"

    cmd = ["ffmpeg"]

    if start_point:
        sp = convert_to_timedelta(start_point)
        if not sp:
            logger.error("Punto de inicio con formato no válido.")
            exit(1)
        cmd.extend(["-ss", str(sp)])

    if end_point:
        ep = convert_to_timedelta(end_point)
        if not ep:
            logger.error("Punto final con formato no válido.")
            exit(1)
        cmd.extend(["-to", str(ep)])

    cmd.extend(["-i", str(path), "-filter_complex", filters, output])

    return cmd
