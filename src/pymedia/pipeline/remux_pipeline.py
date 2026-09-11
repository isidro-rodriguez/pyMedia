"""Subcomando `remux`: remultiplexa un contendor de vídeo."""

from pathlib import Path

from pymedia.errors import (
    MissingParameterError,
)
from pymedia.ffmpeg.remux_cmd import RemuxCmd
from pymedia.locales import _  # noqa
from pymedia.models.parameters import RemuxParameters
from pymedia.pipeline.base_pipeline import BasePipeline
from pymedia.types import OverwriteMode


class RemuxPipeline(BasePipeline[RemuxParameters]):
    """Comando de CLI para remultiplexar un contenedor de vídeo."""

    def process_parameters(
        self,
        media_input: Path,
        media_output: Path,
        overwrite: OverwriteMode,
        fast_start: bool,
        regenerate_pts: bool,
        sort_tracks: bool,
    ) -> None:
        """Valida y parsea los argumentos en parámetros procesados."""
        params = RemuxParameters(
            overwrite=overwrite,
            fast_start=fast_start,
            regenerate_pts=regenerate_pts,
            sort_tracks=sort_tracks,
        )

        params.create_media_input(
            media_input=media_input,
            logger=self.logger,
        )

        params.create_media_output(
            extension=self.config.default_containers.media,
            output=media_output,
            remux=True,
        )

        self.params = params

    def process_cmd(self) -> None:
        """Construye el comando ffmpeg para remux."""
        if self.params.media_output is None:
            raise MissingParameterError(name="media_output")

        if not self.resolve_overwrite(output_list=[self.params.media_output]):
            return

        cmd = RemuxCmd(params=self.params).create()

        self.logger.debug(_("FFmpeg command: %(cmd)s"), cmd=cmd)

        self.run_ffmpeg(
            cmd=cmd,
            description=_("Remuxing media file"),
        )

        self.logger.info(
            msg=_("Container remuxed successfully: %(output)s"),
            output=self.params.media_output,
        )
