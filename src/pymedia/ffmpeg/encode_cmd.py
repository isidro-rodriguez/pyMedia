from pathlib import Path

from pymedia.domain.config import Config
from pymedia.domain.encode_pipeline import EncodePipeline
from pymedia.domain.media_input import MediaInput
from pymedia.utils import parse_crop


def encode_cmd(
    path: Path,
    config: Config,
    media: MediaInput,
    encode_pipeline: EncodePipeline,
    output_name: str | None = None,
):

    video_input = str(path.absolute())
    if output_name is None:
        output_name = path.stem + ".encoded" + path.suffix
    video_output = output_name

    filters = []

    if encode_pipeline.crop is not None:
        if media.video is None:
            raise ValueError(f"Vídeo {path} no encontrado en encode")

        parsed = parse_crop(encode_pipeline.crop)

        if parsed is None:
            raise ValueError(f"Crop {path} no encontrado en encode")

        left, right, top, bottom = parsed

        crop_w = media.video.width - left - right
        crop_h = media.video.height - top - bottom

        filters.append(f"crop={crop_w}:{crop_h}:{left}:{top}")

    if encode_pipeline.scale is not None:
        filters.append(f"scale=-2:{encode_pipeline.scale}")

    if encode_pipeline.gyrate is not None:
        match encode_pipeline.gyrate:
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
