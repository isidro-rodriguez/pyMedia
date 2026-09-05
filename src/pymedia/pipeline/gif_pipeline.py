"""Subcomando `gif`: genera un GIF animado a partir de un vídeo."""

from pathlib import Path

from pymedia.errors import (
    MissingParameterError,
)
from pymedia.ffmpeg.gif_cmd import GifCmd
from pymedia.locales import _  # noqa
from pymedia.models.parameters import GifParameters
from pymedia.pipeline import BasePipeline
from pymedia.types import OverwriteMode, RotateMode, ScaleMode


class GifPipeline(BasePipeline[GifParameters]):
    """Comando de CLI que genera un GIF animado desde el vídeo de entrada."""

    help = _("Generates an animated GIF from the specified video.")

    def process_parameters(
        self,
        media_input: Path,
        overwrite: OverwriteMode,
        fps: int,
        scale_mode: ScaleMode,
        output: Path | None = None,
        timestamp_start: str | None = None,
        timestamp_end: str | None = None,
        crop: str | None = None,
        scale_to: str | None = None,
        scale_upscale: bool = False,
        rotate: RotateMode | None = None,
        hflip: bool = False,
        vflip: bool = False,
    ) -> None:
        """Valida y parsea los argumentos en parámetros procesados."""
        params = GifParameters(
            overwrite=overwrite,
            scale_mode=scale_mode,
            fps=fps,
            hflip=hflip,
            vflip=vflip,
        )

        params.create_media_input(
            media_input=media_input,
            logger=self.logger,
        )

        params.create_animated_output(output=output)

        params.create_crop(
            crop_str=crop,
        )

        params.create_scale(
            logger=self.logger,
            scale_upscale=scale_upscale,
            scale_to=scale_to,
        )

        params.create_rotate(
            rotate=rotate,
        )

        params.create_timestamp_start_end(
            timestamp_start=timestamp_start,
            timestamp_end=timestamp_end,
        )

        self.params = params

    def process_cmd(self) -> None:
        """Construye el comando ffmpeg y ejecuta la generación del GIF."""
        if self.params.media is None:
            raise MissingParameterError(name="media")

        cmd = GifCmd(params=self.params).create()

        self.logger.debug(_("FFmpeg command: %(cmd)s"), cmd=cmd)

        self.run_ffmpeg(
            cmd=cmd,
            description=_("Generating GIF"),
            progress_time=self.params.get_range_time(),
        )

        self.logger.info(
            msg=_("GIF generated successfully: %(output)s"),
            output=self.params.animated_output,
        )
