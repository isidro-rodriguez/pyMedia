"""Comando ``frames``: service."""

from datetime import timedelta
from pathlib import Path

from pymedia.commands.base_service import BaseService
from pymedia.commands.frames.cmd import FramesCmd
from pymedia.commands.frames.parameters import FramesParameters
from pymedia.errors import CommandGenerationError, MissingParameterError
from pymedia.locales import _  # noqa


class FramesService(BaseService[FramesParameters]):
    """Comando de CLI que captura miniaturas en marcas de tiempo concretas."""

    def start(self) -> None:
        """Construye y ejecuta el comando ffmpeg de cada marca indicada.

        Raises:
            MissingParameterError: Si falta el medio, el listado de marcas o la
                ruta de imagen de salida.
            CommandGenerationError: Si el comando ffmpeg no se pudo generar.
        """
        if self.params.media is None:
            raise MissingParameterError(name="media")
        if self.params.timestamp_at is None:
            raise MissingParameterError(name="timestamp_at")

        for timestamp in self.params.timestamp_at:
            cmd = FramesCmd(params=self.params).create(timestamp=timestamp)
            output = self._output_path(timestamp=timestamp)

            # Cada marca es una captura independiente: si su fichero ya existe
            # y no se autoriza la sobrescritura, se omite solo esa marca.
            if not self.resolve_overwrite(output_list=[output]):
                continue

            self._run_cmd(cmd=cmd, output_list=[output])

    def _output_path(self, timestamp: timedelta) -> Path:
        """Devuelve la ruta de salida para un fotograma en timestamp dado.

        Raises:
            MissingParameterError: Si falta la ruta de imagen de salida.
        """
        if self.params.image_output is None:
            raise MissingParameterError(name="image_output")
        return self.params.image_output.with_stem(
            f"{self.params.image_output.stem}_{str(timestamp).replace(':', '-')}"
        )

    def _run_cmd(self, cmd: list[str], output_list: list[Path]) -> None:
        """Ejecuta un comando ffmpeg de miniaturas y registra el resultado.

        Raises:
            CommandGenerationError: Si el comando ffmpeg no se pudo generar.
            MissingParameterError: Si falta el medio.
        """
        if cmd is None:
            raise CommandGenerationError(name=self.command_name)
        if self.params.media is None:
            raise MissingParameterError(name="media")

        self.logger.debug(_("FFmpeg command: %(cmd)s"), cmd=cmd)

        self.run_ffmpeg(
            cmd=cmd,
            progress_time=self.params.get_range_time(),
            description=_("Generating thumbnail"),
            output_list=output_list,
        )

        self.logger.info(
            msg=_("Thumbnail(s) generated successfully: %(output)s"),
            output=self.params.image_output,
        )
