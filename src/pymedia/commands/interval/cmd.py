"""Comando ``interval``: compositor de comandos ffmpeg."""

from pymedia.commands.interval.parameters import IntervalParameters
from pymedia.errors import MissingParameterError
from pymedia.types import OverwriteMode


class IntervalCmd:
    """Compone el comando de ffmpeg para capturas a intervalos regulares."""

    def __init__(self, params: IntervalParameters) -> None:
        """Inicializa el generador con los parámetros validados de interval.

        Args:
            params: Parámetros procesados del comando interval.
        """
        self.params = params

    def create(self) -> list[str]:
        """Compone el comando ffmpeg para extraer fotogramas a intervalos.

        Normaliza `image_output` con el patrón `_%03d` que ffmpeg numera: el
        servicio resuelve las rutas esperadas a partir de ese sufijo.

        Returns:
            Lista de comandos ffmpeg listos para ejecución.

        Raises:
            MissingParameterError: Si falta `image_output`, `fps` o `media`.
        """
        params = self.params
        if params.image_output is None:
            raise MissingParameterError(name="image_output")
        if params.fps is None:
            raise MissingParameterError(name="fps")
        if params.media is None:
            raise MissingParameterError(name="media")

        params.image_output = params.image_output.with_stem(
            f"{params.image_output.stem}_%03d"
        )

        filters: list[str] = [
            "thumbnail=30",
            params.to_fps_cmd(),
            params.to_image_quality_cmd().format,
        ]
        filters_cmd = params.to_filters_cmd()
        if filters_cmd:
            filters.append(filters_cmd)
        filters_str = ",".join(filters)

        cmd: list[str] = ["ffmpeg"]

        if params.overwrite == OverwriteMode.YES:
            cmd.append("-y")

        if params.timestamp_start is not None:
            cmd.extend(params.to_timestamp_start_cmd())
        if params.timestamp_end is not None:
            cmd.extend(params.to_timestamp_end_cmd())

        cmd.extend(
            [
                "-i",
                str(params.media.path),
                "-vf",
                filters_str,
                "-fps_mode",
                "vfr",
                *params.to_image_quality_cmd().compression,
                "-progress",
                "pipe:1",
                "-nostats",
                str(params.image_output),
            ]
        )
        return cmd
