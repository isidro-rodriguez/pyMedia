from pathlib import Path

from pymedia.cli_params import OutputOnConflictMode
from pymedia.models.state import state


def concat_demux_cmd(list_txt: Path):

    cmd = [
        "ffmpeg",
        "-f",
        "concat",
        "-safe",
        "0",
    ]

    if state.output_on_conflict == OutputOnConflictMode.REPLACE:
        cmd.extend(["-y"])

    cmd.extend(
        [
            "-i",
            str(list_txt.absolute()),
            "-c",
            "copy",
            str(state.output),
        ]
    )

    return cmd
