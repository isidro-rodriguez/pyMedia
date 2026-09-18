"""Comando ``add-audio``: service."""

from pymedia.commands.add_audio.cmd import AddAudioCmd
from pymedia.commands.add_audio.parameters import AddAudioParameters
from pymedia.commands.base_service import BaseService
from pymedia.errors import MissingParameterError
from pymedia.locales import _  # noqa


class AddAudioService(BaseService[AddAudioParameters]):
    """Comando de CLI que inserta una pista de audio en un contenedor de vídeo."""

    def start(self) -> None:
        """Construye el comando ffmpeg y ejecuta la inserción de la pista.

        Raises:
            MissingParameterError: Si falta el medio o la salida procesada.
        """
        if self.params.media is None:
            raise MissingParameterError(name="media")
        if self.params.media_output is None:
            raise MissingParameterError(name="media_output")

        if not self.resolve_overwrite(output_list=[self.params.media_output]):
            return

        cmd = AddAudioCmd(params=self.params).create()

        self.logger.debug(_("FFmpeg command: %(cmd)s"), cmd=cmd)

        self.run_ffmpeg(
            cmd=cmd,
            description=_("Adding audio"),
            output_list=[self.params.media_output],
        )

        self.logger.info(
            msg=_("Audio added successfully: %(output)s"),
            output=self.params.media_output,
        )
