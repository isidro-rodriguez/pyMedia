"""Comando ``transcode``: service."""

from pymedia.commands.base_service import BaseService
from pymedia.commands.transcode.cmd import TranscodeCmd
from pymedia.commands.transcode.parameters import TranscodeParameters
from pymedia.errors import MissingParameterError
from pymedia.locales import _  # noqa


class TranscodeService(BaseService[TranscodeParameters]):
    """Comando de CLI para transcodificar un contenedor de vídeo."""

    def start(self) -> None:
        """Construye el comando ffmpeg y ejecuta la transcodificación del contenedor.

        Raises:
            MissingParameterError: Si falta el medio o la salida procesada.
        """
        if self.params.media is None:
            raise MissingParameterError(name="media")
        if self.params.media_output is None:
            raise MissingParameterError(name="media_output")

        if not self.resolve_overwrite(output_list=[self.params.media_output]):
            return

        cmd = TranscodeCmd(params=self.params, config=self.config).create()

        self.logger.debug(_("FFmpeg command: %(cmd)s"), cmd=cmd)

        self.run_ffmpeg(
            cmd=cmd,
            description=_("Transcoding container"),
            progress_time=self.params.media.duration,
            output_list=[self.params.media_output],
        )

        self.logger.info(
            msg=_("Container transcoded successfully: %(output)s"),
            output=self.params.media_output,
        )
