from pathlib import Path

from pymedia.models.state import state


def encode_cmd(
    input_single: Path,
    output: Path,
):

    filters = []
    pipeline = state.video_pipeline
    encode = state.config.encode

    if pipeline.crop:
        filters.append(pipeline.crop)

    if pipeline.scale:
        filters.append(pipeline.scale)

    if pipeline.gyrate:
        filters.append(pipeline.gyrate)

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_single),
    ]

    if filters:
        cmd.extend(["-filter:v", ",".join(filters)])

    cmd.extend(
        [
            "-c:v",
            encode.video_codec,
            "-crf",
            str(encode.video_crf),
            "-preset",
            encode.video_preset,
            "-pix_fmt",
            encode.video_pix_fmt,
            "-c:a",
            "copy",
            str(output),
        ]
    )

    return cmd
