"""Comando ``extract-audio``: service."""

from pymedia.commands.base_service import BaseService
from pymedia.commands.extract_audio.cmd import ExtractAudioCmd
from pymedia.commands.extract_audio.parameters import ExtractAudioParameters
from pymedia.errors import MissingParameterError
from pymedia.locales import _  # noqa


class ExtractAudioService(BaseService[ExtractAudioParameters]):
    """Comando de CLI que extrae pistas de audio a ficheros independientes."""

    def start(self) -> None:
        """Construye el comando ffmpeg y ejecuta la extracción de las pistas.

        Raises:
            MissingParameterError: Si falta el medio.
        """
        if self.params.media is None:
            raise MissingParameterError(name="media")

        cmd, outputs = ExtractAudioCmd(params=self.params).create()

        if not self.resolve_overwrite(output_list=outputs):
            return

        self.logger.debug(_("FFmpeg command: %(cmd)s"), cmd=cmd)

        self.run_ffmpeg(
            cmd=cmd,
            description=_("Extracting audio"),
            output_list=outputs,
        )

        self.logger.info(
            msg=_("Audio extracted successfully: %(output)s"),
            output=self.params.audio_output,
        )
