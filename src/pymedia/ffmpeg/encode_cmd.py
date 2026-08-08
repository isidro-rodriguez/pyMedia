from pathlib import Path

from pymedia.models.config import Config
from pymedia.models.media import Media
from pymedia.models.video_pipeline import VideoPipeline
from pymedia.utils import parse_crop, resolve_output_path


def encode_cmd(
    path: Path,
    media: Media,
    pipeline: VideoPipeline,
    output_name: str | None = None,
):

    config = Config.load()

    video_input = str(path.absolute())
    video_output = str(resolve_output_path(output_name, path, "_encoded"))

    filters = []

    if pipeline.crop is not None:
        if media.video is None:
            raise ValueError(f"Vídeo {path} no encontrado en encode")

        parsed = parse_crop(pipeline.crop)

        if parsed is None:
            raise ValueError(f"Crop {path} no encontrado en encode")

        left, right, top, bottom = parsed

        crop_w = media.video.width - left - right
        crop_h = media.video.height - top - bottom

        filters.append(f"crop={crop_w}:{crop_h}:{left}:{top}")

    if pipeline.scale is not None:
        filters.append(f"scale=-2:{pipeline.scale}")

    if pipeline.gyrate is not None:
        match pipeline.gyrate:
            case 90:
                filters.append("transpose=1")
            case 180:
                filters.append("vflip,hflip")
            case 270:
                filters.append("transpose=2")
            case _:
                return None

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        video_input,
    ]

    if filters:
        cmd.extend(["-filter:v", ",".join(filters)])

    cmd.extend(
        [
            "-c:v",
            config.encode.video_codec,
            "-crf",
            str(config.encode.video_crf),
            "-preset",
            config.encode.video_preset,
            "-pix_fmt",
            config.encode.video_pix_fmt,
            "-c:a",
            "copy",
            video_output,
        ]
    )

    return cmd
