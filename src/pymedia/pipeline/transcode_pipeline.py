"""Subcomando `transcode`: transcodifica un vídeo cambiando su códecs y compresión."""

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
        if not all(
            [
                crop is None,
                scale_to is None,
                rotate is None,
                hflip is False,
                vflip is False,
            ]
        ):
            transcode_video = True

        params = TranscodeParameters(
            overwrite=overwrite,
            transcode=getattr(self.config.transcode, preset_transcode.value),
            transcode_video=transcode_video,
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

        params.create_filters(
            logger=self.logger,
            crop=crop,
            scale_to=scale_to,
            scale_upscale=scale_upscale,
            scale_mode=scale_mode,
            rotate=rotate,
            hflip=hflip,
            vflip=vflip,
        )

        self.params = params

    def process_cmd(self) -> None:
        """Construye el comando ffmpeg y ejecuta la transcodificación del contenedor."""
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
        )

        self.logger.info(
            msg=_("Container transcoded successfully: %(output)s"),
            output=self.params.media_output,
        )
