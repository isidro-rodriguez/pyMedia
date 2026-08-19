from pymedia.models.gif_parameters import GifParameters
from pymedia.typer_options import OutputOnConflictMode


def gif_cmd(params: GifParameters) -> list[str]:
    """
    Composición de cmd ffmpeg para generar un gif.

    Args:
        params: Parámetros validados y parseados obtenidos de los argumentos de CLI.

    Returns:
        cmd: comando de ffmpeg listo para consumo.
    """

    filters: str = ""

    if params.crop:
        filters += f"{params.crop},"
    if params.gyrate:
        filters += f"{params.gyrate},"
    if params.scale:
        filters += f"{params.scale},"

    filters += (
        f"fps={params.fps},split[a][b];[a]palettegen[p];"
        f"[b][p]paletteuse=dither=floyd_steinberg"
    )

    cmd = ["ffmpeg"]

    if params.output_on_conflict == OutputOnConflictMode.REPLACE:
        cmd.extend(["-y"])

    if params.start_point:
        cmd.extend(["-ss", str(params.start_point)])

    if params.end_point:
        cmd.extend(["-to", str(params.end_point)])

    cmd.extend(
        [
            "-i",
            str(params.media.path),
            "-filter_complex",
            filters,
            "-progress",
            "pipe:1",
            "-nostats",
            str(params.output),
        ]
    )

    return cmd
