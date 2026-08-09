from pathlib import Path

from pymedia.models.state import state


def gif_cmd(output: Path) -> list[str]:
    pipeline = state.gif_pipeline
    filters: str = ""

    if pipeline.crop or pipeline.gyrate or pipeline.scale:
        filters_array = []

        if pipeline.crop:
            filters_array.append(pipeline.crop)
        if pipeline.gyrate:
            filters_array.append(pipeline.gyrate)
        if pipeline.scale:
            filters_array.append(pipeline.scale)

        filters = ",".join(filters_array) + ","

    filters += (
        f"fps={pipeline.fps},split[a][b];[a]palettegen[p];"
        f"[b][p]paletteuse=dither=floyd_steinberg"
    )

    cmd = ["ffmpeg"]

    if pipeline.start_point:
        cmd.extend(pipeline.start_point)

    if pipeline.end_point:
        cmd.extend(pipeline.end_point)

    cmd.extend(["-i", str(state.inputs[0]), "-filter_complex", filters, str(output)])

    return cmd
