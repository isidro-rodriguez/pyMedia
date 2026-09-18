"""Subcomando `animated`: genera una imagen animada a partir de un vídeo."""

from pathlib import Path

from pymedia.errors import (
    MissingParameterError,
)
from pymedia.ffmpeg.animated_cmd import AnimatedCmd
from pymedia.locales import _  # noqa
from pymedia.models.parameters import AnimatedParameters
from pymedia.pipeline.base_pipeline import BasePipeline
from pymedia.types import OverwriteMode, RotateMode, ScaleMode


class AnimatedPipeline(BasePipeline[AnimatedParameters]):
    """Comando de CLI que genera una imagen animada desde el vídeo de entrada."""

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
        """Valida y parsea los argumentos en parámetros procesados.

        Args:
            media_input: Ruta del fichero de vídeo a procesar.
            overwrite: Política ante conflicto de salida ya existente.
            fps: Fotogramas por segundo de la imagen animada generado.
            scale_mode: Política de escalado del vídeo o imagen.
            output: Ruta absoluta del fichero de salida procesado.
            timestamp_start: Marca de tiempo que indica el punto inicial.
            timestamp_end: Marca de tiempo que indica el punto final.
            crop: Área y coordenada de la zona a preservar de la imagen.
            scale_to: Dimensión objetivo en píxeles.
            scale_upscale: Permite el incremento de dimensiones.
            rotate: Ángulo ortogonal con el que se va a rotar la imagen.
            hflip: Invierte la imagen horizontalmente.
            vflip: Invierte la imagen verticalmente.
        """
        params = AnimatedParameters(
            overwrite=overwrite,
            fps=fps,
        )

        params.create_media_input(
            media_input=media_input,
            logger=self.logger,
        )

        params.create_animated_output(
            output=output,
            extension=self.config.default_containers.animated_image,
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

        params.create_timestamp_start_end(
            timestamp_start=timestamp_start,
            timestamp_end=timestamp_end,
        )

        self.params = params

    def process_cmd(self) -> None:
        """Construye el comando ffmpeg y ejecuta la generación de una imagen animada.

        Raises:
            MissingParameterError: Si no se obtuvo el medio o la salida animada.
        """
        if self.params.media is None:
            raise MissingParameterError(name="media")
        if self.params.animated_output is None:
            raise MissingParameterError(name="animated_output")

        if not self.resolve_overwrite(output_list=[self.params.animated_output]):
            return

        cmd = AnimatedCmd(params=self.params).create()

        self.logger.debug(_("FFmpeg command: %(cmd)s"), cmd=cmd)

        self.run_ffmpeg(
            cmd=cmd,
            description=_("Generating animated image"),
            progress_time=self.params.get_range_time(),
            output_list=[self.params.animated_output],
        )

        self.logger.info(
            msg=_("Animated image generated successfully: %(output)s"),
            output=self.params.animated_output,
        )
