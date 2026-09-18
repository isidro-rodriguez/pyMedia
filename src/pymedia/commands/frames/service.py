"""Comando ``frames``: service."""

from pathlib import Path

from pymedia.commands.base_service import BaseService
from pymedia.commands.frames.cmd import FramesCmd
from pymedia.commands.frames.parameters import FramesParameters
from pymedia.errors import MissingParameterError
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
            if self.params.image_output is None:
                raise MissingParameterError(name="image_output")
            output = Path(
                f"{self.params.image_output.stem}_{str(timestamp).replace(':', '-')}"
            )

            if not self.resolve_overwrite(output_list=[output]):
                continue

            self.logger.debug(_("FFmpeg command: %(cmd)s"), cmd=cmd)

            self.run_ffmpeg(
                cmd=cmd,
                progress_time=self.params.get_range_time(),
                description=_("Generating thumbnail"),
                output_list=[output],
            )

            self.logger.info(
                msg=_("Thumbnail(s) generated successfully: %(output)s"),
                output=self.params.image_output,
            )
