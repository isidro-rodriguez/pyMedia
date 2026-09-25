"""Comando ``delete-subs``: service."""

from pymedia.commands.base_service import BaseService
from pymedia.commands.delete_subtitles.cmd import DeleteSubtitlesCmd
from pymedia.commands.delete_subtitles.parameters import DeleteSubtitlesParameters
from pymedia.errors import MissingParameterError
from pymedia.locales import translate as _


class DeleteSubtitlesService(BaseService[DeleteSubtitlesParameters]):
    """Comando de CLI que elimina pistas de subtítulos de un contenedor."""

    def start(self) -> None:
        """Construye el comando ffmpeg y ejecuta la eliminación de las pistas.

        Raises:
            MissingParameterError: Si falta el medio o la salida procesada.
        """
        if self.params.media is None:
            raise MissingParameterError(name="media")
        if self.params.media_output is None:
            raise MissingParameterError(name="media_output")

        if not self.resolve_overwrite(output_list=[self.params.media_output]):
            return

        cmd = DeleteSubtitlesCmd(params=self.params).create()

        self.display_cmd(cmd=cmd)

        self.run_ffmpeg(
            cmd=cmd,
            description=_("Deleting subtitles"),
            output_list=[self.params.media_output],
        )

        self.logger.info(
            msg=_("Subtitles deleted successfully: %(output)s"),
            output=self.params.media_output,
        )
