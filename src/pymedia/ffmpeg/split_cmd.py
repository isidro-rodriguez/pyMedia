from pathlib import Path

from pymedia.cli_params import OutputOnConflictMode
from pymedia.models.state import state


def split_cmd(
    input_single: Path,
    output: Path,
):

    cmd = ["ffmpeg"]

    if state.output_on_conflict == OutputOnConflictMode.REPLACE:
        cmd.extend(["-y"])

    cmd.extend(
        [
            "-i",
            str(input_single.absolute()),
            "-map",
            "0",
            "-c",
            "copy",
            "-f",
            "segment",
            "-reset_timestamps",
            "1",
            "-segment_times",
            state.video_pipeline.trim_points,
            "-progress",
            "pipe:1",
            "-nostats",
            str(output),
        ]
    )

    return cmd
