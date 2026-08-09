from pathlib import Path

from pymedia.models.state import state


def concat_demux_cmd(list_txt: Path):

    cmd = [
        "ffmpeg",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(list_txt.absolute()),
        "-c",
        "copy",
        str(state.output),
    ]

    return cmd
