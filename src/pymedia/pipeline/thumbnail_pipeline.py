"""Subcomando `thumbnail`: genera una o varias miniaturas desde un vídeo."""

from pymedia.data.types import OverwriteMode, ScaleMode
from pymedia.errors import (
    CommandGenerationError,
    MissingMediaError,
    MissingParameterError,
)
from pymedia.ffmpeg.thumbnail_cmd import ThumbnailCmd
from pymedia.locales import _  # noqa
from pymedia.models.pipeline.thumbnail_pipeline import (
    ThumbnailArguments,
    ThumbnailParameters,
)
from pymedia.pipeline.base_pipeline import BasePipeline, SinglePipeline
from pymedia.typer.options import (
    CropOption,
    DebugOption,
    EveryOption,
    FlipHorizontalOption,
    FlipVerticalOption,
    HelpOption,
    InputSingleArgument,
    OutputOption,
    OverwriteOption,
    RotateOption,
    ScaleModeOption,
    ScaleToOption,
    ScaleUpscaleOption,
    SceneOption,
    TimestampAtThumbnailOption,
    TimestampEndGifOption,
    TimestampStartGifOption,
)


class ThumbnailCommand(SinglePipeline[ThumbnailArguments, ThumbnailParameters]):
    """Comando de CLI que genera miniaturas en modos timestamp, intervalo o escena."""

    command_name = "thumbnail"
    help = _("Generates an animated GIF from the specified video.")

    @staticmethod
    def cli(
        input_single: InputSingleArgument,
        output: OutputOption = None,
        overwrite: OverwriteOption = OverwriteMode.ASK,
        every: EveryOption = None,
        scene: SceneOption = None,
        timestamp_at: TimestampAtThumbnailOption = None,
        timestamp_start: TimestampStartGifOption = None,
        timestamp_end: TimestampEndGifOption = None,
        crop: CropOption = None,
        rotate: RotateOption = None,
        scale_to: ScaleToOption = None,
        scale_mode: ScaleModeOption = ScaleMode.FIT,
        scale_upscale: ScaleUpscaleOption = False,
        hflip: FlipHorizontalOption = False,
        vflip: FlipVerticalOption = False,
        debug: DebugOption = False,
        help_: HelpOption = False,
    ) -> None:
        """Punto de entrada de Typer: construye los argumentos y ejecuta el comando.

        Args:
            input_single: Vídeo de entrada.
            output: Ruta de salida (por defecto, se deriva de la entrada).
            overwrite: Política ante un fichero de salida existente.
            every: Intervalo en segundos entre imágenes (modo intervalo).
            scene: Umbral de sensibilidad para detección de cambio de escena
                (modo escena).
            timestamp_at: Lista de marcas de tiempo (modo timestamp).
            timestamp_start: Marca temporal del punto inicial.
            timestamp_end: Marca temporal del punto final.
            crop: Área a recortar (WIDTH,HEIGHT,X,Y).
            rotate: Ángulo ortogonal con el que se va a rotar la imagen (90, 180 o 270).
            scale_to: Dimensión objetivo (WIDTHxHEIGHT).
            scale_mode: Modo de escalado (STRETCH, FIT o COVER).
            scale_upscale: Permite escalar por encima del tamaño original.
            hflip: Voltea horizontalmente.
            vflip: Voltea verticalmente.
            debug: Habilita el nivel de log DEBUG.
            help_: Muestra la ayuda del comando.
        """
        ThumbnailCommand.run(
            args=BasePipeline.build_args(
                args_cls=ThumbnailArguments,
                local_vars=locals(),
            ),
            debug=debug,
        )

    def process_parameters(self) -> None:
        """Valida y parsea los argumentos en parámetros procesados."""
        self.params = ThumbnailParameters.create(args=self.args, logger=self.logger)

    def process_cmd(self) -> None:
        """Construye y ejecuta los comandos ffmpeg de las miniaturas."""
        if self.params.input_single is None:
            raise MissingParameterError(name="input_single")
        if self.params.media is None:
            raise MissingMediaError(path=str(self.params.input_single))

        if self.params.timestamp_at is not None:
            for timestamp in self.params.timestamp_at:
                cmd = ThumbnailCmd(params=self.params).create(timestamp=timestamp)
                self._run_cmd(cmd=cmd)
        else:
            cmd = ThumbnailCmd(params=self.params).create()
            self._run_cmd(cmd=cmd)

    def _run_cmd(self, cmd: list[str]) -> None:
        """Ejecuta un comando ffmpeg de miniaturas y registra el resultado."""
        if cmd is None:
            raise CommandGenerationError(name=self.command_name)

        if self.params.media is None:
            raise MissingParameterError(name="media")

        self.logger.debug(_("FFmpeg command: %(cmd)s"), cmd=cmd)

        progress_time = self.resolve_progress_time(
            video_duration=self.media.duration,
            timestamp_start=self.params.timestamp_start,
            timestamp_end=self.params.timestamp_end,
        )

        self.run_ffmpeg(
            cmd=cmd,
            progress_time=progress_time,
            description=_("Generating thumbnail"),
            stall_timeout=self.config.app.stall_timeout,
            command_name=self.command_name,
        )

        self.logger.info(
            msg=_("Thumbnail(s) generated successfully: %(output)s"),
            output=self.params.output,
        )
