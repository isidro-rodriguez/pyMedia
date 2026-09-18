"""Comando ``edit-subs``: service."""

from pymedia.commands.base_service import BaseService
from pymedia.commands.edit_subtitles.cmd import EditSubtitlesCmd
from pymedia.commands.edit_subtitles.parameters import EditSubtitlesParameters
from pymedia.errors import MissingParameterError
from pymedia.locales import _  # noqa


class EditSubtitlesService(BaseService[EditSubtitlesParameters]):
    """Comando de CLI que edita los metadatos de una pista de subtítulos."""

    def start(self) -> None:
        """Construye el comando ffmpeg y ejecuta la edición de metadatos.

        Raises:
            MissingParameterError: Si falta el medio o la salida procesada.
        """
        if self.params.media is None:
            raise MissingParameterError(name="media")
        if self.params.media_output is None:
            raise MissingParameterError(name="media_output")

        if not self.resolve_overwrite(output_list=[self.params.media_output]):
            return

        cmd = EditSubtitlesCmd(params=self.params).create()

        self.logger.debug(_("FFmpeg command: %(cmd)s"), cmd=cmd)

        self.run_ffmpeg(
            cmd=cmd,
            description=_("Editing subtitles metadata"),
            output_list=[self.params.media_output],
        )

        self.logger.info(
            msg=_("Subtitles metadata edited successfully: %(output)s"),
            output=self.params.media_output,
        )
