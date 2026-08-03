from pathlib import Path

from pymedia.domain.config import Config
from pymedia.domain.media_input import MediaInput
from pymedia.domain.transcoding_pipeline import TranscodingPipeline
from pymedia.utils import parse_crop


def transcode_cmd(
    path: Path,
    config: Config,
    media: MediaInput,
    transcoding_pipeline: TranscodingPipeline,
):

    video_input = path.absolute()
    video_output = path.name + ".transcoded" + path.suffix

    filters = []

    if transcoding_pipeline.crop:
        if media.video is None:
            raise ValueError(f"Vídeo {path} no encontrado en transcode")

        parsed = parse_crop(transcoding_pipeline.crop)

        if parsed is None:
            raise ValueError(f"Crop {path} no encontrado en transcode")

        left, right, top, bottom = parsed

        crop_w = media.video.width - left - right
        crop_h = media.video.height - top - bottom
        crop_x = left
        crop_y = top

        filters.append(f"crop={crop_w}:{crop_h}:{crop_x}:{crop_y}")

    if transcoding_pipeline.scale:
        filters.append(f"scale=-2:{transcoding_pipeline.scale}")

    if transcoding_pipeline.gyrate:
        match transcoding_pipeline.gyrate:
            case 90:
                filters.append("transpose=1")
            case 180:
                filters.append("vflip,hflip")
            case 270:
                filters.append("transpose=2")
            case _:
                return None

    if filters:
        return [
            "ffmpeg",
            "-i",
            video_input,
            "-filter:v",
            ",".join(filters),
            "-c:v",
            config.transcode.video_codec,
            "-crf",
            config.transcode.video_crf,
            "-preset",
            config.transcode.video_preset,
            "-c:a",
            "copy",
            video_output,
        ]

    return [
        "ffmpeg",
        "-i",
        video_input,
        "-c:v",
        config.transcode.video_codec,
        "-crf",
        config.transcode.video_crf,
        "-preset",
        config.transcode.video_preset,
        "-c:a",
        "copy",
        video_output,
    ]
