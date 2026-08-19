from pathlib import Path

from pymedia.models._state import state

from pymedia.data.video_codecs import VIDEO_CODECS
from pymedia.typer_options import OutputOnConflictMode


def encode_cmd(
    input_single: Path,
    output: Path,
):

    filters = []
    pipeline = state.video_pipeline
    encode = state.config.encode
    index = state.inputs.index(input_single)

    if pipeline.crop:
        filters.append(pipeline.crop[index])

    if pipeline.gyrate:
        filters.append(pipeline.gyrate)

    if pipeline.scale:
        filters.append(pipeline.scale[index])

    cmd = ["ffmpeg"]

    if state.output_on_conflict == OutputOnConflictMode.REPLACE:
        cmd.extend(["-y"])

    cmd.extend(
        [
            "-i",
            str(input_single),
        ]
    )

    if filters:
        cmd.extend(["-filter:v", ",".join(filters)])

    cmd.extend(
        [
            "-c:v",
            VIDEO_CODECS[state.config.encode.video_codec].library,
            "-crf",
            str(encode.video_crf),
            "-preset",
            encode.video_preset,
            "-pix_fmt",
            VIDEO_CODECS[state.config.encode.video_codec].pix_fmt,
            "-c:a",
            "copy",
            "-progress",
            "pipe:1",
            "-nostats",
            str(output),
        ]
    )

    return cmd
