"""Comando ``frames``: cli."""

import typer

from pymedia.commands.base_cli_options import (
    CropOption,
    DebugOption,
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
    TimestampAtThumbnailOption,
)
from pymedia.commands.frames.parameters import FramesParameters
from pymedia.commands.frames.service import FramesService
from pymedia.errors import MissingRequiredOptionsError
from pymedia.locales import _  # noqa
from pymedia.logger import Logger
from pymedia.types import OverwriteMode, ScaleMode

frames_cli = typer.Typer()

FRAMES_HELP = _(
    """\
Captures video frames at the specified timestamps.

[bold]Examples[/bold]:
  Capture a single thumbnail at a given time:
    > pymedia frames input.mp4 --at 00:01:30
  Capture thumbnails at several timestamps:
    > pymedia frames input.mp4 --at 00:01:30,00:05:15
  Save to a specific file:
    > pymedia frames input.mp4 --at 00:01:30 --output thumb.jpg
"""
)


@frames_cli.command(
    name="frames",
    help=FRAMES_HELP,
    rich_help_panel=_("Image commands"),
    no_args_is_help=True,
)
def frames(
    media_input: MediaInputArgument,
    output: OutputOption = None,
    overwrite: OverwriteOption = OverwriteMode.ASK,
    timestamp_at: TimestampAtThumbnailOption = None,
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
    """Punto de entrada del comando ``frames``.

    Args:
        media_input: Ruta del fichero de vídeo a procesar.
        output: Ruta absoluta del fichero de salida procesado.
        overwrite: Política ante conflicto de salida ya existente.
        timestamp_at: Lista de marcas de tiempo.
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
        InvalidArgumentError: Si el formato del listado de marcas no es válido.
        InvalidContainerError: Si la extensión no es una imagen soportada.
        InvalidParameterError: Si el formato de imagen no está soportado.
        InvalidTimeFormatError: Si alguna marca no tiene un formato válido.
        MissingParameterError: Si falta el medio, el listado de marcas o la
            ruta de imagen de salida.
        MissingPropertyError: Si el medio no declara alguna propiedad técnica.
        PermissionDeniedError: Si no se puede crear el directorio de salida.
        UserError: Si una marca supera la duración del vídeo o el nombre de
            salida contiene caracteres no permitidos.
    """
    if timestamp_at is None:
        raise MissingRequiredOptionsError(options=["at"])

    Logger.create(debug=debug)
    if not timestamp_at:
        raise MissingRequiredOptionsError(options=["at"])
    params = FramesParameters.load(
        overwrite=overwrite,
        media_input=media_input,
        output=output,
        timestamp_at=timestamp_at,
        crop=crop,
        rotate=rotate,
        scale_to=scale_to,
        scale_mode=scale_mode,
        scale_upscale=scale_upscale,
        hflip=hflip,
        vflip=vflip,
    )
    FramesService(debug=debug, params=params).start()
