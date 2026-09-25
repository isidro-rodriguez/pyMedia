"""Comando ``remux``: service."""

from pymedia.commands.base_service import BaseService
from pymedia.commands.remux.cmd import RemuxCmd
from pymedia.commands.remux.parameters import RemuxParameters
from pymedia.errors import MissingParameterError
from pymedia.locales import translate as _


class RemuxService(BaseService[RemuxParameters]):
    """Comando de CLI para remultiplexar un contenedor de vídeo."""

    def start(self) -> None:
        """Construye el comando ffmpeg y ejecuta el remultiplexado.

        Raises:
            MissingParameterError: Si la salida procesada no se pudo obtener.
        """
        if self.params.media_output is None:
            raise MissingParameterError(name="media_output")

        if not self.resolve_overwrite(output_list=[self.params.media_output]):
            return

        cmd = RemuxCmd(params=self.params).create()

        self.display_cmd(cmd=cmd)

        self.run_ffmpeg(
            cmd=cmd,
            description=_("Remuxing media file"),
            output_list=[self.params.media_output],
        )

        self.logger.info(
            msg=_("Container remuxed successfully: %(output)s"),
            output=self.params.media_output,
        )
