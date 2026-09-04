"""Subcomando `thumbnail`: genera una o varias miniaturas desde un vídeo."""

from pathlib import Path

from pymedia.errors import (
    CommandGenerationError,
    ExclusiveOptionsError,
    MissingMediaError,
    MissingParameterError,
    MissingRequiredOptionError,
)
from pymedia.ffmpeg.screenshoot_cmd import ScreenshootCmd
from pymedia.locales import _  # noqa
from pymedia.models.parameters import ScreenshootParameters
from pymedia.pipeline import BasePipeline
from pymedia.types import OutputMediaType, OverwriteMode, RotateMode, ScaleMode


class ScreenshootPipeline(BasePipeline[ScreenshootParameters]):
    """Comando de CLI que genera miniaturas en modos timestamp, intervalo o escena."""

    def process_parameters(
        self,
        input_single: Path,
        output: Path | None = None,
        overwrite: OverwriteMode = OverwriteMode.ASK,
        every: int | None = None,
        scene: float | None = None,
        timestamp_at: str | None = None,
        timestamp_start: str | None = None,
        timestamp_end: str | None = None,
        crop: str | None = None,
        rotate: RotateMode | None = None,
        scale_to: str | None = None,
        scale_mode: ScaleMode = ScaleMode.FIT,
        scale_upscale: bool = False,
        hflip: bool = False,
        vflip: bool = False,
    ) -> None:
        """Valida y parsea los argumentos en parámetros procesados.

        Attributes:
            input_single: Ruta del fichero de vídeo a procesar.
            output: Ruta absoluta del fichero de salida procesado.
            overwrite: Política ante conflicto de salida ya existente.
            every: Periodo, en segundos, entre capturas generadas.
            scene: Umbral de sensibilidad para detección de cambio de escena.
            timestamp_at: Lista de marcas de tiempo.
            timestamp_start: Marca de tiempo que indica el punto inicial.
            timestamp_end: Marca de tiempo que indica el punto final.
            crop: Área y coordenada de la zona a preservar de la imagen.
            rotate: Ángulo ortogonal con el que se va a rotar la imagen.
            scale_to: Dimensión objetivo en píxeles.
            scale_mode: Política de escalado del vídeo o imagen.
            scale_upscale: Permite el incremento de dimensiones.
            hflip: Invierte la imagen horizontalmente, intercambia izquierda y derecha.
            vflip: Invierte la imagen verticalmente, intercambiando arriba y abajo.
        """
        params = ScreenshootParameters(
            overwrite=overwrite,
            scale_mode=scale_mode,
            hflip=hflip,
            vflip=vflip,
        )

        params.create_input_single(
            input_single=input_single,
            logger=self.logger,
        )

        params.create_output(
            media_type=OutputMediaType.IMAGE,
            output=output,
            affix="_thumbnail",
            extension=".jpg",
        )

        params.create_timestamp_at(
            times_str=timestamp_at,
        )

        params.create_timestamp_start_end(
            timestamp_start=timestamp_start,
            timestamp_end=timestamp_end,
        )

        params.create_scene(
            scene=scene,
        )

        params.create_fps(
            every=every,
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
        """Construye y ejecuta los comandos ffmpeg de las miniaturas."""
        if self.params.input_single is None:
            raise MissingParameterError(name="input_single")
        if self.params.media is None:
            raise MissingMediaError(path=str(self.params.input_single))

        if self.params.timestamp_at is not None:
            for timestamp in self.params.timestamp_at:
                cmd = ScreenshootCmd(params=self.params).create(timestamp=timestamp)
                self._run_cmd(cmd=cmd)
        else:
            cmd = ScreenshootCmd(params=self.params).create()
            self._run_cmd(cmd=cmd)

    def _run_cmd(self, cmd: list[str]) -> None:
        """Ejecuta un comando ffmpeg de miniaturas y registra el resultado."""
        if cmd is None:
            raise CommandGenerationError(name=self.command_name)

        if self.params.media is None:
            raise MissingParameterError(name="media")

        self.logger.debug(_("FFmpeg command: %(cmd)s"), cmd=cmd)

        progress_time = self.resolve_progress_time(params=self.params)

        self.run_ffmpeg(
            cmd=cmd,
            progress_time=progress_time,
            description=_("Generating thumbnail"),
        )

        self.logger.info(
            msg=_("Thumbnail(s) generated successfully: %(output)s"),
            output=self.params.output,
        )

    def _validate_options(self) -> None:
        """Verifica las opciones requeridas y descarta combinaciones ambiguas."""
        params = self.params
        at, scene, fps = params.timestamp_at, params.scene, params.fps
        start, end = params.timestamp_start, params.timestamp_end

        # 1. Al menos uno debe existir (evaluando presencia explícita)
        if not any(x is not None for x in (at, scene, fps)):
            raise MissingRequiredOptionError(options=["--at", "--scene", "--every"])

        # 2. Exclusividad mutua (máximo 1 de las opciones principales)
        if sum(x is not None for x in (at, scene, fps)) > 1:
            raise ExclusiveOptionsError(options=["--at", "--scene", "--every"])

        # 3. Conflicto entre --at y rango (--timestamp_start / --timestamp_end)
        if at is not None and any(x is not None for x in (start, end)):
            raise ExclusiveOptionsError(
                option="--at",
                incompatible_with=["--timestamp_start", "--timestamp_end"],
            )
