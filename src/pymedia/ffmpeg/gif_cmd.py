from pymedia.errors import MissingParameterError
from pymedia.models.enums import OutputOnConflictMode
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

    if params.fps is None:
        raise MissingParameterError(parameter="fps")

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
