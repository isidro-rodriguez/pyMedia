"""Comando ``scene``: cli."""

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
    SceneOption,
    ShowCmdOption,
    TimestampEndThumbnailOption,
    TimestampStartThumbnailOption,
)
from pymedia.commands.scene.parameters import SceneParameters
from pymedia.commands.scene.service import SceneService
from pymedia.locales import translate as _
from pymedia.logger import Logger
from pymedia.types import OverwriteMode, ScaleMode

scene_cli = typer.Typer()

SCENE_HELP = _(
    """\
Captures video frames when the image changes significantly following a shot transition.

Captures images when a change in framing causes the image to change by more
than the user-defined threshold, expressed as a value between 0 and 1.

[bold]Examples[/bold]:
  Detect scene changes with default sensitivity:
    > pymedia scene input.mp4
  Adjust the scene-change sensitivity:
    > pymedia scene input.mp4 --scene 0.3
  Limit the search to a time range:
    > pymedia scene input.mp4 --start 00:00:05 --end 00:00:30
  Save to a specific file:
    > pymedia scene input.mp4 --output thumb.jpg
"""
)


@scene_cli.command(
    name="scene",
    help=SCENE_HELP,
    rich_help_panel=_("Image commands"),
    no_args_is_help=True,
)
def scene(
    media_input: MediaInputArgument,
    output: OutputOption = None,
    overwrite: OverwriteOption = OverwriteMode.ASK,
    scene: SceneOption = 0.3,
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
    show_cmd: ShowCmdOption = False,
    help_: HelpOption = False,
) -> None:
    """Punto de entrada del comando ``scene``.

    Args:
        media_input: Ruta del fichero de vídeo a procesar.
        output: Ruta absoluta del fichero de salida procesado.
        overwrite: Política ante conflicto de salida ya existente.
        scene: Umbral de sensibilidad para detección de cambio de escena.
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
        show_cmd: Muestra al usuario el comando ffmpeg compuesto pero no lo ejecuta.
        help_: Helper para mostrar esta línea en distintos idiomas.

    Raises:
        InvalidContainerError: Si la extensión no es una imagen soportada.
        InvalidParameterError: Si el formato de imagen no está soportado o la
            marca de inicio es posterior a la de fin.
        InvalidTimeFormatError: Si alguna marca no tiene un formato válido.
        MissingParameterError: Si falta el medio, el umbral de escena o la ruta
            de imagen de salida.
        MissingPropertyError: Si el medio no declara alguna propiedad técnica.
        PermissionDeniedError: Si no se puede crear el directorio de salida.
        UserError: Si una marca supera la duración del vídeo o el nombre de
            salida contiene caracteres no permitidos.
    """
    Logger.create(debug=debug)
    params = SceneParameters.load(
        overwrite=overwrite,
        media_input=media_input,
        output=output,
        scene=scene,
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
    SceneService(debug=debug, show_cmd=show_cmd, params=params).start()
