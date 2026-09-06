"""Pipeline del comando `subtitles add`."""

from pathlib import Path

from pymedia.errors import MissingParameterError
from pymedia.ffmpeg.subtitles_add_cmd import SubtitlesAddCmd
from pymedia.locales import _  # noqa
from pymedia.models.parameters import SubtitlesAddParameters
from pymedia.pipeline.base_pipeline import BasePipeline
from pymedia.types import OverwriteMode


class SubtitlesAddPipeline(BasePipeline[SubtitlesAddParameters]):
    """Comando de CLI que genera un GIF animado desde el vídeo de entrada."""

    def process_parameters(
        self,
        media_input: Path,
        overwrite: OverwriteMode,
        subtitles_input: Path,
        subtitles_language: str,
        media_output: Path | None = None,
        subtitles_title: str | None = None,
        subtitles_forced: bool = False,
        subtitles_default: bool = False,
        subtitles_hearing_impaired: bool = False,
        subtitles_visual_impaired: bool = False,
    ) -> None:
        """Valida y parsea los argumentos en parámetros procesados."""
        params = SubtitlesAddParameters(
            overwrite=overwrite,
        )

        params.create_media_input(
            media_input=media_input,
            logger=self.logger,
        )

        params.create_media_output(
            extension=media_input.suffix,
            affix="_subtitled",
            output=media_output,
        )

        params.create_subtitle(
            subtitles_input=subtitles_input.absolute(),
            language=subtitles_language,
            logger=self.logger,
            title=subtitles_title,
            forced=subtitles_forced,
            default=subtitles_default,
            hearing_impaired=subtitles_hearing_impaired,
            visual_impaired=subtitles_visual_impaired,
        )

        self.params = params

    def process_cmd(self) -> None:
        """Construye el comando ffmpeg y ejecuta la generación del GIF."""
        if self.params.media is None:
            raise MissingParameterError(name="media")

        cmd = SubtitlesAddCmd(params=self.params).create()

        self.logger.debug(_("FFmpeg command: %(cmd)s"), cmd=cmd)

        self.run_ffmpeg(
            cmd=cmd,
            description=_("Adding subtitles"),
        )

        self.logger.info(
            msg=_("Subtitles added successfully: %(output)s"),
            output=self.params.media_output,
        )
