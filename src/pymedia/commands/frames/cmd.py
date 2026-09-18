"""Comando ``frames``: compositor de comandos ffmpeg."""

from datetime import timedelta

from pymedia.commands.frames.parameters import FramesParameters
from pymedia.errors import MissingParameterError
from pymedia.types import OverwriteMode


class FramesCmd:
    """Compone el comando de ffmpeg para capturar un fotograma en una marca."""

    def __init__(self, params: FramesParameters) -> None:
        """Inicializa el generador con los parámetros validados de frames.

        Args:
            params: Parámetros procesados del comando frames.
        """
        self.params = params

    def create(self, timestamp: timedelta) -> list[str]:
        """Compone el comando ffmpeg para extraer un fotograma en un instante dado.

        Args:
            timestamp: Marca de tiempo del fotograma a capturar.

        Returns:
            Lista de comandos ffmpeg listos para ejecución.

        Raises:
            MissingParameterError: Si falta `image_output` o `media`.
        """
        params = self.params
        if params.image_output is None:
            raise MissingParameterError(name="image_output")
        if params.media is None:
            raise MissingParameterError(name="media")

        output = params.image_output.with_stem(
            f"{params.image_output.stem}_{str(timestamp).replace(':', '-')}"
        )

        filters: list[str] = [
            "thumbnail=30",
            params.to_image_quality_cmd().format,
        ]
        filters_cmd = params.to_filters_cmd()
        if filters_cmd:
            filters.append(filters_cmd)
        filters_str = ",".join(filters)

        cmd: list[str] = ["ffmpeg"]

        if params.overwrite == OverwriteMode.YES:
            cmd.append("-y")
        else:
            cmd.append("-n")

        cmd.extend(["-ss", str(timestamp)])

        cmd.extend(
            [
                "-i",
                str(params.media.path),
                "-vf",
                filters_str,
                "-frames:v",
                "1",
                *params.to_image_quality_cmd().compression,
                "-progress",
                "pipe:1",
                "-nostats",
                str(output),
            ]
        )

        return cmd
