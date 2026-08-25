from pymedia.models.enums import OverwriteMode
from pymedia.models.pipeline.gif_pipeline import GifParameters


def gif_cmd(params: GifParameters) -> list[str]:
    """Composición de llamada ffmpeg para generar un Gif.

    Args:
        params: Parámetros validados y parseados obtenidos de los argumentos de CLI.

    Returns:
        cmd: comando de ffmpeg listo para consumo.
    """

    filters: str = ""

    if params.resize_width or params.resize_height:
        filters += params.to_resize_cmd() + ","

    filters += (
        f"{params.to_fps_cmd()},split[a][b];[a]palettegen[p];"
        f"[b][p]paletteuse=dither=floyd_steinberg"
    )

    cmd = ["ffmpeg"]

    if params.overwrite == OverwriteMode.YES:
        cmd.extend(["-y"])

    if params.timestamp_start:
        cmd.extend(params.to_timestamp_start_cmd())

    if params.timestamp_end:
        cmd.extend(params.to_timestamp_end_cmd())

    cmd.extend(
        [
            *params.to_input_single_cmd(),
            "-filter_complex",
            filters,
            "-progress",
            "pipe:1",
            "-nostats",
            str(params.output),
        ]
    )

    return cmd
