"""Comando ``interval``: service."""

import math
from pathlib import Path

import typer

from pymedia.commands.base_service import BaseService
from pymedia.commands.interval.cmd import IntervalCmd
from pymedia.commands.interval.parameters import IntervalParameters
from pymedia.errors import CommandGenerationError, MissingParameterError
from pymedia.locales import _  # noqa
from pymedia.types import OverwriteMode


class IntervalService(BaseService[IntervalParameters]):
    """Comando de CLI que captura miniaturas a intervalos regulares."""

    def start(self) -> None:
        """Construye y ejecuta el comando ffmpeg de capturas periódicas.

        Raises:
            MissingParameterError: Si falta el medio, el periodo, la duración
                del medio o la ruta de imagen de salida.
            CommandGenerationError: Si el comando ffmpeg no se pudo generar.
        """
        if self.params.media is None:
            raise MissingParameterError(name="media")

        cmd = IntervalCmd(params=self.params).create()

        # `create` normaliza `image_output` con el patrón `_%03d`: la lista de
        # salidas esperadas se resuelve después sobre ese sufijo.
        output_list = self._output_list()

        # En `ask` se pregunta por cada fichero de la lista; con `yes`/`no`,
        # ffmpeg aplica `-y`/`-n` sobre el patrón numerado.
        if self.params.overwrite == OverwriteMode.ASK and not self._confirm_overwrite(
            output_list=output_list
        ):
            return

        self._run_cmd(cmd=cmd, output_list=output_list)

    def _output_list(self) -> list[Path]:
        """Genera la lista de salidas esperadas del patrón numerado.

        Raises:
            MissingParameterError: Si falta la imagen de salida, la duración
                del medio o el periodo de captura.
        """
        params = self.params
        output = params.image_output
        if output is None:
            raise MissingParameterError(name="image_output")
        media = params.media
        if media is None or media.duration is None:
            raise MissingParameterError(name="media.duration")
        fps = params.fps
        if fps is None:
            raise MissingParameterError(name="fps")

        frames = media.duration.total_seconds() * float(fps)
        return [
            Path(str(output).replace("_%03d", f"_{i:3d}"))
            for i in range(math.floor(frames))
        ]

    def _confirm_overwrite(self, output_list: list[Path]) -> bool:
        """Pregunta al usuario por cada archivo existente en la lista."""
        for output in output_list:
            if output.exists():
                self.logger.warning(_(f"Output file already exists: {output.name}"))
                if not typer.confirm(_("Overwrite?")):
                    self.logger.warning(
                        _("Process skipped since output file already exists.")
                    )
                    return False
        return True

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
