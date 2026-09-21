"""Comando ``edit-audio``: service."""

from pymedia.commands.base_service import BaseService
from pymedia.commands.edit_audio.cmd import EditAudioCmd
from pymedia.commands.edit_audio.parameters import EditAudioParameters
from pymedia.errors import MissingParameterError
from pymedia.locales import _


class EditAudioService(BaseService[EditAudioParameters]):
    """Comando de CLI que edita los metadatos de una pista de audio."""

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

        cmd = EditAudioCmd(params=self.params).create()

        self.logger.debug(_("FFmpeg command: %(cmd)s"), cmd=cmd)

        self.run_ffmpeg(
            cmd=cmd,
            description=_("Editing audio metadata"),
            output_list=[self.params.media_output],
        )

        self.logger.info(
            msg=_("Audio metadata edited successfully: %(output)s"),
            output=self.params.media_output,
        )
