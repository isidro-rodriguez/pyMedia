"""Composición de comandos ffmpeg para el subcomando thumbnail."""

from datetime import timedelta

from pymedia.errors import MissingParameterError
from pymedia.models.parameters import ThumbParameters
from pymedia.types import OverwriteMode


class ThumbCmd:
    """Compone los comandos ffmpeg para generar thumbnails."""

    def __init__(self, params: ThumbParameters) -> None:
        """Inicializa el generador y resuelve el modo de thumbnail.

        Args:
            params: Parámetros procesados del subcomando thumbnail.
        """
        self.params = params

    def create_frames_cmd(self, timestamp: timedelta) -> list[str]:
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

        # Construir filtros
        filters: list[str] = [
            "thumbnail=30",
            params.to_image_quality_cmd().format,
        ]
        filters_cmd = params.to_filters_cmd()
        if filters_cmd:
            filters.append(filters_cmd)
        filters_str = ",".join(filters)

        cmd: list[str] = ["ffmpeg"]

        if self.params.overwrite is OverwriteMode.YES:
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

    def create_interval_cmd(self) -> list[str]:
        """Compone el comando ffmpeg para extraer fotogramas a intervalos regulares.

        Returns:
            Lista de comandos ffmpeg listos para ejecución (ffmpeg numera la salida).

        Raises:
            MissingParameterError: Si falta `image_output`, `fps` o `media`.
        """
        params = self.params
        if params.image_output is None:
            raise MissingParameterError(name="image_output")
        if params.media is None:
            raise MissingParameterError(name="media")

        params.image_output = params.image_output.with_stem(
            f"{params.image_output.stem}_%03d"
        )

        # Construir filtros
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

        if self.params.overwrite is OverwriteMode.YES:
            cmd.append("-y")
        else:
            cmd.append("-n")

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

    def create_scene_cmd(self) -> list[str]:
        """Compone el comando ffmpeg para extraer fotogramas en cambios de escena.

        Returns:
            Lista de comandos ffmpeg listos para ejecución (ffmpeg numera la salida).

        Raises:
            MissingParameterError: Si falta `image_output`, `scene` o `media`.
        """
        params = self.params
        if params.image_output is None:
            raise MissingParameterError(name="image_output")
        if params.media is None:
            raise MissingParameterError(name="media")

        output = params.image_output.with_stem(f"{params.image_output.stem}_%03d")

        # Construir filtros
        filters: list[str] = [
            params.to_scene_cmd(),
            params.to_image_quality_cmd().format,
        ]
        filters_cmd = params.to_filters_cmd()
        if filters_cmd:
            filters.append(filters_cmd)
        filters_str = ",".join(filters)

        cmd: list[str] = ["ffmpeg"]

        if self.params.overwrite is OverwriteMode.YES:
            cmd.append("-y")
        else:
            cmd.append("-n")

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
                str(output),
            ]
        )
        return cmd
