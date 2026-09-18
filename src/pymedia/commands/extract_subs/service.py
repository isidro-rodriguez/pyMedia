"""Comando ``extract-subs``: service."""

from pymedia.commands.base_service import BaseService
from pymedia.commands.extract_subs.cmd import ExtractSubtitlesCmd
from pymedia.commands.extract_subs.parameters import ExtractSubtitlesParameters
from pymedia.errors import MissingParameterError
from pymedia.locales import _  # noqa


class ExtractSubtitlesService(BaseService[ExtractSubtitlesParameters]):
    """Comando de CLI que extrae pistas de subtítulos a ficheros independientes."""

    def start(self) -> None:
        """Construye el comando ffmpeg y ejecuta la extracción de las pistas.

        Raises:
            MissingParameterError: Si falta el medio.
        """
        if self.params.media is None:
            raise MissingParameterError(name="media")

        cmd, outputs = ExtractSubtitlesCmd(params=self.params).create()

        if not self.resolve_overwrite(output_list=outputs):
            return

        self.logger.debug(_("FFmpeg command: %(cmd)s"), cmd=cmd)

        self.run_ffmpeg(
            cmd=cmd,
            description=_("Extracting subtitles"),
            output_list=outputs,
        )

        self.logger.info(
            msg=_("Subtitles extracted successfully: %(output)s"),
            output=self.params.subtitles_output,
        )
