from pathlib import Path


def concat_demux_cmd(list_txt: Path, output: Path):

    cmd = ["ffmpeg", "-f", "concat", "-safe", "0", "-i", list_txt, "-c", "copy", output]

    return cmd
