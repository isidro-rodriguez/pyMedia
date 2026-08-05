from pathlib import Path

from pymedia.domain.encode_pipeline import EncodePipeline
from pymedia.domain.media_input import MediaInput
from pymedia.logger import get_logger
from pymedia.utils import convert_to_timedelta, parse_crop

logger = get_logger("gif")


def _build_filters(
    media: MediaInput, fps: int, scale: int, crop: str | None, gyrate: int | None
) -> str:
    encode_filters = []

    if crop:
        parse_crop(crop)
        if media.video is None:
            raise ValueError("Vídeo no encontrado en encode")

        parsed = parse_crop(crop)

        if parsed is None:
            raise ValueError("Crop no encontrado en encode")

        left, right, top, bottom = parsed

        crop_w = media.video.width - left - right
        crop_h = media.video.height - top - bottom

        encode_filters.append(f"crop={crop_w}:{crop_h}:{left}:{top}")
    if gyrate:
        match gyrate:
            case 90:
                encode_filters.append("transpose=1")
            case 180:
                encode_filters.append("vflip,hflip")
            case 270:
                encode_filters.append("transpose=2")
    if scale:
        # int(scale) resuelve enums tipo ScaleGifMode(int, Enum) a su valor numérico
        encode_filters.append(f"scale=-2:{int(scale)}:flags=lanczos")

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
    pipeline: EncodePipeline,
    media: MediaInput,
    fps: int | None = None,
    start_point: str | None = None,
    end_point: str | None = None,
    output_name: str | None = None,
) -> list[str]:

    assert fps
    assert pipeline.scale

    filters: str = _build_filters(
        media, fps, pipeline.scale, pipeline.crop, pipeline.gyrate
    )

    if output_name:
        if output_name.endswith(".gif"):
            output = output_name
        else:
            output = path.stem + ".gif"
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
