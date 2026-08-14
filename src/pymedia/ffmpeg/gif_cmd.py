from pathlib import Path

from pymedia.cli_params import OutputOnConflictMode
from pymedia.models.state import state


def gif_cmd(output: Path) -> list[str]:
    pipeline = state.gif_pipeline
    filters: str = ""

    if pipeline.crop:
        filters += pipeline.crop[0] + ","
    if pipeline.gyrate:
        filters += pipeline.gyrate + ","
    if pipeline.scale != [None]:
        filters += pipeline.scale[0] + ","

    filters += (
        f"fps={pipeline.fps},split[a][b];[a]palettegen[p];"
        f"[b][p]paletteuse=dither=floyd_steinberg"
    )

    cmd = ["ffmpeg"]

    if state.output_on_conflict == OutputOnConflictMode.REPLACE:
        cmd.extend(["-y"])

    if pipeline.start_point:
        cmd.extend(["-ss", str(pipeline.start_point)])

    if pipeline.end_point:
        cmd.extend(["-t", str(pipeline.end_point)])

    cmd.extend(
        [
            "-i",
            str(state.inputs[0]),
            "-filter_complex",
            filters,
            "-progress",
            "pipe:1",
            "-nostats",
            str(output),
        ]
    )

    return cmd
