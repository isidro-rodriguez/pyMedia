from pymedia.errors import MissingParameterError
from pymedia.models.enums import OverwriteMode
from pymedia.models.pipeline.gif_pipeline import GifParameters


def gif_cmd(params: GifParameters) -> list[str]:
    """Composición de llamada ffmpeg para generar un Gif.

    Args:
        params: Parámetros validados y parseados obtenidos de los argumentos de CLI.

    Returns:
        cmd: comando de ffmpeg listo para consumo.
    """
    if params.output is None:
        raise MissingParameterError(name="output")

    filters: list[str] = []

    if params.crop_area is not None:
        crop_filter = params.to_crop_cmd()
        if crop_filter is not None:
            filters.append(f"{crop_filter}")

    if params.scale_to is not None:
        scale_filter = params.to_scale_cmd()
        if scale_filter is not None:
            filters.append(f"{scale_filter}")

    if params.rotate is not None:
        rotate_filter = params.to_rotate_cmd()
        if rotate_filter is not None:
            filters.append(f"{rotate_filter}")

    filters.append(f"{params.to_fps_cmd()}")

    filters.append(
        "split[a][b];[a]palettegen[p];[b][p]paletteuse=dither=floyd_steinberg"
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
            ",".join(filters),
            "-progress",
            "pipe:1",
            "-nostats",
            str(params.output),
        ]
    )

    return cmd
