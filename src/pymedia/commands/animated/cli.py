"""Comando ``animated``: cli."""

import typer

from pymedia.commands.animated.parameters import AnimatedParameters
from pymedia.commands.animated.service import AnimatedService
from pymedia.commands.base_cli_options import (
    CropOption,
    DebugOption,
    FlipHorizontalOption,
    FlipVerticalOption,
    FpsAnimatedOption,
    HelpOption,
    MediaInputArgument,
    OutputOption,
    OverwriteOption,
    RotateOption,
    ScaleModeOption,
    ScaleToOption,
    ScaleUpscaleOption,
    ShowCmdOption,
    TimestampEndAnimatedOption,
    TimestampStartAnimatedOption,
)
from pymedia.locales import translate as _
from pymedia.logger import Logger
from pymedia.types import OverwriteMode, ScaleMode

animated_cli = typer.Typer()

ANIMATED_HELP = _(
    """\
Generates an animated image from the specified video.

[bold]Examples[/bold]:
  Convert a video to an animated image:
    > pymedia animated input.mp4
  Convert a time range:
    > pymedia animated input.mp4 --start 00:00:05 --end 00:00:12
  Set size and frame rate:
    > pymedia animated input.mp4 --size 480x270 --fps 15
  Save to a specific file:
    > pymedia animated input.mp4 --output output.gif
"""
)


@animated_cli.command(
    name="animated",
    help=ANIMATED_HELP,
    rich_help_panel=_("Image commands"),
    no_args_is_help=True,
)
def animated(
    media_input: MediaInputArgument,
    output: OutputOption = None,
    overwrite: OverwriteOption = OverwriteMode.ASK,
    timestamp_start: TimestampStartAnimatedOption = None,
    timestamp_end: TimestampEndAnimatedOption = None,
    fps: FpsAnimatedOption = 12,
    crop: CropOption = None,
    rotate: RotateOption = None,
    scale_to: ScaleToOption = "640x360",
    scale_mode: ScaleModeOption = ScaleMode.FIT,
    scale_upscale: ScaleUpscaleOption = False,
    hflip: FlipHorizontalOption = False,
    vflip: FlipVerticalOption = False,
    debug: DebugOption = False,
    show_cmd: ShowCmdOption = False,
    help_: HelpOption = False,
) -> None:
    """Punto de entrada del comando ``animated``.

    Args:
        media_input: Ruta del fichero de vídeo a procesar.
        output: Ruta absoluta del fichero de salida procesado.
        overwrite: Política ante conflicto de salida ya existente.
        timestamp_start: Marca de tiempo que indica el punto inicial.
        timestamp_end: Marca de tiempo que indica el punto final.
        fps: Imágenes por segundo de la imagen animada.
        crop: Área y coordenada de la zona a preservar de la imagen.
        rotate: Ángulo ortogonal con el que se va a rotar la imagen.
        scale_to: Dimensión objetivo en píxeles.
        scale_mode: Política de escalado del vídeo o imagen.
        scale_upscale: Permite el incremento de dimensiones.
        hflip: Invierte la imagen horizontalmente, intercambia izquierda y derecha.
        vflip: Invierte la imagen verticalmente, intercambiando arriba y abajo.
        debug: Habilita el nivel de log DEBUG.
        show_cmd: Muestra al usuario el comando ffmpeg compuesto pero no lo ejecuta.
        help_: Helper para mostrar esta línea en distintos idiomas.
    """
    Logger.create(debug=debug)
    params = AnimatedParameters.load(
        overwrite=overwrite,
        media_input=media_input,
        output=output,
        timestamp_start=timestamp_start,
        timestamp_end=timestamp_end,
        fps=fps,
        crop=crop,
        rotate=rotate,
        scale_to=scale_to,
        scale_mode=scale_mode,
        scale_upscale=scale_upscale,
        hflip=hflip,
        vflip=vflip,
        show_cmd=show_cmd,
    )
    AnimatedService(debug=debug, show_cmd=show_cmd, params=params).start()
