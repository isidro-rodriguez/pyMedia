"""Comandos de la familia thumbnails."""

import typer

from pymedia.locales import _  # noqa
from pymedia.pipeline.thumb_pipeline import ThumbPipeline
from pymedia.typer.instance import typer_instance
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
from pymedia.types import OverwriteMode, ScaleMode

# =============================================================================
#  Subcomando FRAMES
# =============================================================================

_HELP_FRAMES = _(
    """\
Captures thumbnails at the specified timestamps.

[bold]Examples[/bold]:
  Capture a single thumbnail at a given time:
    > pymedia frames input.mp4 --at 00:01:30
  Capture thumbnails at several timestamps:
    > pymedia frames input.mp4 --at 00:01:30,00:05:15
  Save to a specific file:
    > pymedia frames input.mp4 --at 00:01:30 --output thumb.jpg
"""
)


frames_command = typer.Typer(
    name="frames",
    help=_HELP_FRAMES,
    no_args_is_help=True,
)


@frames_command.callback(invoke_without_command=True)
def _frames_run(
    input_single: InputSingleArgument,
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
    """Punto de entrada de Typer: construye los argumentos y ejecuta el comando.

    Args:
        input_single: Ruta del fichero de vídeo a procesar.
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
    """
    pipeline = ThumbPipeline(debug=debug)
    pipeline.process_parameters(
        input_single=input_single,
        output=output,
        overwrite=overwrite,
        timestamp_at=timestamp_at,
        crop=crop,
        rotate=rotate,
        scale_to=scale_to,
        scale_mode=scale_mode,
        scale_upscale=scale_upscale,
        hflip=hflip,
        vflip=vflip,
    )
    if not pipeline.resolve_overwrite():
        return
    pipeline.process_cmd()


# =============================================================================
#  Subcomando INTERVAL
# =============================================================================

_HELP_INTERVAL = _(
    """\
Captures thumbnails at regular intervals of the video.

[bold]Examples[/bold]:
  Capture a thumbnail every second:
    > pymedia interval input.mp4 --every 1
  Capture a thumbnail every 5 seconds within a time range:
    > pymedia interval input.mp4 --every 5 --start 00:00:10 --end 00:01:00
  Save to a specific file:
    > pymedia interval input.mp4 --every 5 --output thumb.jpg
"""
)
interval_command = typer.Typer(
    name="interval",
    help=_HELP_INTERVAL,
    no_args_is_help=True,
)


@interval_command.callback(invoke_without_command=True)
def _interval_run(
    input_single: InputSingleArgument,
    output: OutputOption = None,
    overwrite: OverwriteOption = OverwriteMode.ASK,
    every: EveryOption = None,
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
    help_: HelpOption = False,  # noqa
) -> None:
    """Punto de entrada de Typer: construye los argumentos y ejecuta el comando.

    Args:
        input_single: Ruta del fichero de vídeo a procesar.
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
    """
    pipeline = ThumbPipeline(debug=debug)
    pipeline.process_parameters(
        input_single=input_single,
        output=output,
        overwrite=overwrite,
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
    if not pipeline.resolve_overwrite():
        return
    pipeline.process_cmd()


if __name__ == "__main__":
    typer_instance()

# =============================================================================
#  Subcomando SCENE
# =============================================================================

_HELP_SCENE = _(
    """\
Captures thumbnails at the scene changes detected in the video.

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
scene_command = typer.Typer(
    name="scene",
    help=_HELP_SCENE,
    no_args_is_help=True,
)


@scene_command.callback(invoke_without_command=True)
def _scene_run(
    input_single: InputSingleArgument,
    output: OutputOption = None,
    overwrite: OverwriteOption = OverwriteMode.ASK,
    scene: SceneOption = None,
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
    help_: HelpOption = False,  # noqa
) -> None:
    """Punto de entrada de Typer: construye los argumentos y ejecuta el comando.

    Args:
        input_single: Ruta del fichero de vídeo a procesar.
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
        help_: Helper para mostrar esta línea en distintos idiomas.
    """
    pipeline = ThumbPipeline(debug=debug)
    pipeline.process_parameters(
        input_single=input_single,
        output=output,
        overwrite=overwrite,
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
    if not pipeline.resolve_overwrite():
        return
    pipeline.process_cmd()
