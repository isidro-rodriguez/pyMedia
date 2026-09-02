"""Subcomando `gif`: genera un GIF animado a partir de un vídeo."""

from pymedia.commands.base_command import BaseCommand, SingleCommand
from pymedia.data.types import OverwriteMode, ScaleMode
from pymedia.errors import (
    CommandGenerationError,
    MissingMediaError,
    MissingParameterError,
)
from pymedia.ffmpeg.gif_cmd import GifCmd
from pymedia.locales import _  # noqa
from pymedia.models.pipeline.gif_pipeline import GifArguments, GifParameters
from pymedia.typer_options import (
    CropOption,
    DebugOption,
    FlipHorizontalOption,
    FlipVerticalOption,
    FpsGifOption,
    HelpOption,
    InputSingleArgument,
    OutputOption,
    OverwriteOption,
    RotateOption,
    ScaleModeOption,
    ScaleToOption,
    ScaleUpscaleOption,
    TimestampEndGifOption,
    TimestampStartGifOption,
)


class GifCommand(SingleCommand[GifArguments, GifParameters]):
    """Comando de CLI que genera un GIF animado desde el vídeo de entrada."""

    name = "gif"
    help = _("Generates an animated GIF from the specified video.")

    @staticmethod
    def cli(
        input_single: InputSingleArgument,
        output: OutputOption = None,
        overwrite: OverwriteOption = OverwriteMode.ASK,
        timestamp_start: TimestampStartGifOption = None,
        timestamp_end: TimestampEndGifOption = None,
        fps: FpsGifOption = 12,
        crop: CropOption = None,
        rotate: RotateOption = None,
        scale_to: ScaleToOption = "640x360",
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
            timestamp_start: Marca temporal del punto inicial.
            timestamp_end: Marca temporal del punto final.
            fps: Imágenes por segundo del GIF.
            crop: Área a recortar (WIDTH,HEIGHT,X,Y).
            rotate: Ángulo de rotación (90, 180 o 270).
            scale_to: Dimensión objetivo (WIDTHxHEIGHT).
            scale_mode: Modo de escalado (STRETCH, FIT o COVER).
            scale_upscale: Permite escalar por encima del tamaño original.
            hflip: Voltea horizontalmente.
            vflip: Voltea verticalmente.
            debug: Habilita el nivel de log DEBUG.
            help_: Muestra la ayuda del comando.
        """
        GifCommand.run(
            args=BaseCommand.build_args(
                args_cls=GifArguments,
                local_vars=locals(),
            ),
            debug=debug,
        )

    def process_parameters(self) -> None:
        """Valida y parsea los argumentos en parámetros procesados."""
        self.params = GifParameters.create(args=self.args, logger=self.logger)

    def process_cmd(self) -> None:
        """Construye el comando ffmpeg y ejecuta la generación del GIF."""
        if self.params.input_single is None:
            raise MissingParameterError(name="input_single")
        if self.params.media is None:
            raise MissingMediaError(path=str(self.params.input_single))
        cmd = GifCmd(params=self.params).create()
        if cmd is None:
            raise CommandGenerationError(name=self.name)
        self.cmd = cmd

        self.logger.debug(_("FFmpeg command: %(cmd)s"), cmd=self.cmd)

        self.run_ffmpeg(
            cmd=self.cmd,
            media=self.params.media,
            description=_("Generating GIF"),
            stall_timeout=self.config.app.stall_timeout,
            command_name=self.name,
        )

        self.logger.info(
            _("GIF generated successfully: %(output)s"), output=self.params.output
        )
