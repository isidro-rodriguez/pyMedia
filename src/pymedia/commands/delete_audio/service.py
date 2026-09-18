"""Comando ``delete-audio``: service."""

from pymedia.commands.base_service import BaseService
from pymedia.commands.delete_audio.cmd import DeleteAudioCmd
from pymedia.commands.delete_audio.parameters import DeleteAudioParameters
from pymedia.errors import MissingParameterError
from pymedia.locales import _  # noqa


class DeleteAudioService(BaseService[DeleteAudioParameters]):
    """Comando de CLI que elimina pistas de audio de un contenedor de vídeo."""

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

        cmd = DeleteAudioCmd(params=self.params).create()

        self.logger.debug(_("FFmpeg command: %(cmd)s"), cmd=cmd)

        self.run_ffmpeg(
            cmd=cmd,
            description=_("Deleting audio"),
            output_list=[self.params.media_output],
        )

        self.logger.info(
            msg=_("Audio deleted successfully: %(output)s"),
            output=self.params.media_output,
        )
