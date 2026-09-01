from pymedia.data.types import OverwriteMode
from pymedia.errors import MissingParameterError
from pymedia.models.pipeline.gif_pipeline import GifParameters


def gif_cmd(params: GifParameters) -> list[str]:
    """Composición de llamada ffmpeg para generar un Gif.

    Args:
        params: Parámetros validados y parseados obtenidos de los argumentos de CLI.

    Returns:
        cmd: comando de ffmpeg listo para consumo.
    """

    def _build_filters() -> str:
        """Construye los filtros de ffmpeg para generar un Gif."""
        filters: list[str] = []

        if params.crop_area is not None:
            filters.append(params.to_crop_cmd())

        if params.scale_to is not None:
            scale_filter = params.to_scale_cmd()
            if scale_filter is not None:
                filters.append(scale_filter)

        if params.hflip or params.vflip:
            filters.append(params.to_flip_cmd())

        if params.rotate is not None:
            filters.append(params.to_rotate_cmd())

        filters.append(params.to_fps_cmd())

        filters.append(
            "split[a][b];[a]palettegen[p];[b][p]paletteuse=dither=floyd_steinberg"
        )

        return ",".join(filters)

    if params.output is None:
        raise MissingParameterError(name="output")

    filters_str: str = _build_filters()

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
            filters_str,
            "-progress",
            "pipe:1",
            "-nostats",
            str(params.output),
        ]
    )

    return cmd
