from datetime import timedelta
from pathlib import Path

from pymedia.utils import resolve_output_path


def split_cmd(
    path: Path,
    trim_points: list[timedelta],
    output_name: str | None = None,
):

    video_input = str(path.absolute())

    segment_times = ",".join(str(t.total_seconds()) for t in trim_points)

    output_path = resolve_output_path(output_name, path, "_split")
    video_outputs = str(
        output_path.parent / (output_path.stem + "_%02d" + output_path.suffix)
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        video_input,
        "-map",
        "0",
        "-c",
        "copy",
        "-f",
        "segment",
        "-reset_timestamps",
        "1",
        "-segment_times",
        segment_times,
        video_outputs,
    ]

    return cmd
