"""Subcomando `gif`: genera un GIF animado a partir de un vídeo."""

from pathlib import Path

from pymedia.errors import (
    MissingParameterError,
)
from pymedia.ffmpeg.transcode_cmd import TranscodeCmd
from pymedia.locales import _  # noqa
from pymedia.models.parameters import TranscodeParameters
from pymedia.pipeline.base_pipeline import BasePipeline
from pymedia.types import (
    OverwriteMode,
    PresetsTranscodeMode,
    RotateMode,
    ScaleMode,
    StreamsMode,
)


class TranscodePipeline(BasePipeline[TranscodeParameters]):
    """Comando de CLI para transcodificar un contenedor de vídeo."""

    def process_parameters(
        self,
        media_input: Path,
        overwrite: OverwriteMode,
        preset_transcode: PresetsTranscodeMode,
        scale_mode: ScaleMode,
        output: Path | None = None,
        output_directory: Path | None = None,
        transcode_audio: str | None = None,
        transcode_video: bool = False,
        crop: str | None = None,
        scale_to: str | None = None,
        scale_upscale: bool = False,
        rotate: RotateMode | None = None,
        hflip: bool = False,
        vflip: bool = False,
    ) -> None:
        """Valida y parsea los argumentos en parámetros procesados."""
        params = TranscodeParameters(
            overwrite=overwrite,
            scale_mode=scale_mode,
            hflip=hflip,
            vflip=vflip,
        )

        params.create_media_input(
            media_input=media_input,
            logger=self.logger,
        )

        params.create_media_output(
            extension=self.config.default_containers.media,
            affix="_transcoded",
            output=output,
            output_directory=output_directory,
        )

        params.create_streams(
            stream_tracks=transcode_audio,
            streams_type=StreamsMode.AUDIO,
        )

        params.create_transcode(
            mode=preset_transcode,
            video=transcode_video,
        )

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

        self.params = params

    def process_cmd(self) -> None:
        """Construye el comando ffmpeg y ejecuta la transcodificación del contenedor."""
        if self.params.media is None:
            raise MissingParameterError(name="media")

        cmd = TranscodeCmd(params=self.params).create()

        self.logger.debug(_("FFmpeg command: %(cmd)s"), cmd=cmd)

        self.run_ffmpeg(
            cmd=cmd,
            description=_("Transcoding container"),
            progress_time=self.params.media.duration,
        )

        self.logger.info(
            msg=_("Container transcoded successfully: %(output)s"),
            output=self.params.media_output,
        )
