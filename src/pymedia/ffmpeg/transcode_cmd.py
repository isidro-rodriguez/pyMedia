from pathlib import Path

from pymedia.domain.config import Config
from pymedia.domain.transcoding_pipeline import TranscodingPipeline


def transcode_cmd(
    path: Path, config: Config, transcoding_pipeline: TranscodingPipeline
):

    input = path.absolute()
    output = path.name + ".transcoded" + path.suffix

    filters = []

    if transcoding_pipeline.gyrate:
        match transcoding_pipeline.gyrate:
            case 90:
                filters.append("transpose=1")
            case 180:
                filters.append("vflip,hflip")
            case 270:
                filters.append("transpose=0")
            case _:
                return

    if transcoding_pipeline.crop:
        filters.append("crop")

    if transcoding_pipeline.scale:
        filters.append(f"scale=-2:{transcoding_pipeline.scale}")

    if filters:
        filters.insert(0, "-filter:v")

    return [
        "ffmpeg",
        "-i",
        input,
        filters,
        "-c:v",
        config.transcode.video_codec,
        "-crf",
        config.transcode.video_crf,
        "-preset",
        config.transcode.video_preset,
        "-c:a",
        "copy",
        output,
    ]
