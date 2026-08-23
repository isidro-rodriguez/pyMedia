from pymedia.models.enums import OverwriteMode
from pymedia.models.gif_model import GifParameters
from pymedia.services.ffmpeg_service import scale_to_cmd


def gif_cmd(params: GifParameters) -> list[str]:
    """
    Composición de cmd ffmpeg para generar un gif.

    Args:
        params: Parámetros validados y parseados obtenidos de los argumentos de CLI.

    Returns:
        cmd: comando de ffmpeg listo para consumo.
    """

    filters: str = ""

    if params.scale:
        filters += scale_to_cmd(scale=params.scale) + ","

    filters += (
        f"fps={params.fps},split[a][b];[a]palettegen[p];"
        f"[b][p]paletteuse=dither=floyd_steinberg"
    )

    cmd = ["ffmpeg"]

    if params.overwrite == OverwriteMode.YES:
        cmd.extend(["-y"])

    if params.timestamp_start:
        cmd.extend(["-ss", str(params.timestamp_start)])

    if params.timestamp_end:
        cmd.extend(["-to", str(params.timestamp_end)])

    cmd.extend(
        [
            "-i",
            str(params.input_single),
            "-filter_complex",
            filters,
            "-progress",
            "pipe:1",
            "-nostats",
            str(params.output),
        ]
    )

    return cmd
