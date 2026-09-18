"""Comando ``scene``: compositor de comandos ffmpeg."""

from pymedia.commands.scene.parameters import SceneParameters
from pymedia.errors import MissingParameterError
from pymedia.types import OverwriteMode


class SceneCmd:
    """Compone el comando de ffmpeg para capturas en cambios de escena."""

    def __init__(self, params: SceneParameters) -> None:
        """Inicializa el generador con los parámetros validados de scene.

        Args:
            params: Parámetros procesados del comando scene.
        """
        self.params = params

    def create(self) -> list[str]:
        """Compone el comando ffmpeg para extraer fotogramas por cambio de escena.

        Returns:
            Lista de comandos ffmpeg listos para ejecución (ffmpeg numera la
            salida).

        Raises:
            MissingParameterError: Si falta `image_output`, `scene` o `media`.
        """
        params = self.params
        if params.image_output is None:
            raise MissingParameterError(name="image_output")
        if params.media is None:
            raise MissingParameterError(name="media")

        output = params.image_output.with_stem(f"{params.image_output.stem}_%03d")

        filters: list[str] = [
            params.to_scene_cmd(),
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
                str(output),
            ]
        )
        return cmd
