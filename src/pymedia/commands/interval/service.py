"""Comando ``interval``: service."""

import math
from pathlib import Path

from pymedia.commands.base_service import BaseService
from pymedia.commands.interval.cmd import IntervalCmd
from pymedia.commands.interval.parameters import IntervalParameters
from pymedia.errors import MissingParameterError
from pymedia.locales import _


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
        output_list = self._expected_outputs()

        if not self.resolve_overwrite(output_list=output_list):
            return

        self.display_cmd(cmd=cmd)

        self.run_ffmpeg(
            cmd=cmd,
            progress_time=self.params.get_range_time(),
            description=_("Generating thumbnail"),
            output_list=output_list,
        )

        self.logger.info(
            msg=_("Thumbnail(s) generated successfully: %(output)s"),
            output=str(self.params.image_output).replace("%03d", "*"),
        )

    def _expected_outputs(self) -> list[Path]:
        """Genera la lista de salidas esperadas del patrón numerado."""
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
            Path(str(output).replace("_%03d", f"_{i:03d}"))
            for i in range(1, math.floor(frames) + 1)
        ]
