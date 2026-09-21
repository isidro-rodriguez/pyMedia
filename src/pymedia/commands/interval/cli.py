"""Comando ``interval``: cli."""

import typer

from pymedia.commands.base_cli_options import (
    CropOption,
    DebugOption,
    EveryOption,
    FlipHorizontalOption,
    FlipVerticalOption,
    HelpOption,
    MediaInputArgument,
    OutputOption,
    OverwriteOption,
    RotateOption,
    ScaleModeOption,
    ScaleToOption,
    ScaleUpscaleOption,
    TimestampEndThumbnailOption,
    TimestampStartThumbnailOption,
)
from pymedia.commands.interval.parameters import IntervalParameters
from pymedia.commands.interval.service import IntervalService
from pymedia.errors import MissingRequiredOptionsError, UserError
from pymedia.locales import _
from pymedia.logger import Logger
from pymedia.types import OverwriteMode, ScaleMode

interval_cli = typer.Typer()

INTERVAL_HELP = _(
    """\
Captures video frames at regular intervals.

[bold]Examples[/bold]:
  Capture a thumbnail every minute:
    > pymedia interval input.mp4 --every 60
  Capture a thumbnail every 5 seconds within a time range:
    > pymedia interval input.mp4 --every 5 --start 00:00:10 --end 00:01:00
  Save to a specific file:
    > pymedia interval input.mp4 --every 5 --output thumb.jpg
"""
)


@interval_cli.command(
    name="interval",
    help=INTERVAL_HELP,
    rich_help_panel=_("Image commands"),
    no_args_is_help=True,
)
def interval(
    media_input: MediaInputArgument,
    output: OutputOption = None,
    overwrite: OverwriteOption = OverwriteMode.ASK,
    every: EveryOption = None,
    timestamp_start: TimestampStartThumbnailOption = None,
    timestamp_end: TimestampEndThumbnailOption = None,
    crop: CropOption = None,
    rotate: RotateOption = None,
    scale_to: ScaleToOption = None,
    scale_mode: ScaleModeOption = ScaleMode.FIT,
    scale_upscale: ScaleUpscaleOption = False,
    hflip: FlipHorizontalOption = False,
    vflip: FlipVerticalOption = False,
    debug: DebugOption = False,
    help_: HelpOption = False,  # noqa
) -> None:
    """Punto de entrada del comando ``interval``.

    Args:
        media_input: Ruta del fichero de vídeo a procesar.
        output: Ruta absoluta del fichero de salida procesado.
        overwrite: Política ante conflicto de salida ya existente.
        every: Periodo, en segundos, entre capturas generadas.
        timestamp_start: Marca de tiempo que indica el punto inicial.
        timestamp_end: Marca de tiempo que indica el punto final.
        crop: Área y coordenada de la zona a preservar de la imagen.
        rotate: Ángulo ortogonal con el que se va a rotar la imagen.
        scale_to: Dimensión objetivo en píxeles.
        scale_mode: Política de escalado del vídeo o imagen.
        scale_upscale: Permite el incremento de dimensiones.
        hflip: Invierte la imagen horizontalmente, intercambia izquierda y derecha.
        vflip: Invierte la imagen verticalmente, intercambiando arriba y abajo.
        debug: Habilita el nivel de log DEBUG.
        help_: Helper para mostrar esta línea en distintos idiomas.

    Raises:
        InvalidContainerError: Si la extensión no es una imagen soportada.
        InvalidParameterError: Si el formato de imagen no está soportado o la
            marca de inicio es posterior a la de fin.
        InvalidTimeFormatError: Si alguna marca no tiene un formato válido.
        MissingParameterError: Si falta el medio, el periodo o la ruta de
            imagen de salida.
        MissingPropertyError: Si el medio no declara su duración.
        PermissionDeniedError: Si no se puede crear el directorio de salida.
        UserError: Si una marca supera la duración del vídeo o el nombre de
            salida contiene caracteres no permitidos.
    """
    Logger.create(debug=debug)
    if every is None:
        raise MissingRequiredOptionsError(options=["every"])
    if every < 1:
        raise UserError(msg=_("Interval must be at least 1 second."))
    params = IntervalParameters.load(
        overwrite=overwrite,
        media_input=media_input,
        output=output,
        every=every,
        timestamp_start=timestamp_start,
        timestamp_end=timestamp_end,
        crop=crop,
        rotate=rotate,
        scale_to=scale_to,
        scale_mode=scale_mode,
        scale_upscale=scale_upscale,
        hflip=hflip,
        vflip=vflip,
    )
    IntervalService(debug=debug, params=params).start()
