"""Subcomandos de la familia screenshoot."""

import typer

from pymedia.locales import _  # noqa
from pymedia.pipeline.screenshoot_pipeline import ScreenshootPipeline
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

screenshoot = typer.Typer(
    help=_(
        """\
Captures thumbnails from a video using scene detection, timestamps, or intervals.

[bold]Subcommands[/bold]:
  scene      Detects scene changes and captures a thumbnail at each one.
  frames     Captures thumbnails at specific timestamps.
  interval   Captures thumbnails at regular intervals.
"""
    ),
    no_args_is_help=True,
)

_HELP_SCENE = _(
    """\
Captures thumbnails at the scene changes detected in the video.

[bold]Examples[/bold]:
  Detect scene changes with default sensitivity:
    > pymedia screenshoot scene input.mp4
  Adjust the scene-change sensitivity:
    > pymedia screenshoot scene input.mp4 --scene 0.3
  Limit the search to a time range:
    > pymedia screenshoot scene input.mp4 --start 00:00:05 --end 00:00:30
  Save to a specific file:
    > pymedia screenshoot scene input.mp4 --output thumb.jpg
"""
)


_HELP_FRAMES = _(
    """\
Captures thumbnails at the specified timestamps.

[bold]Examples[/bold]:
  Capture a single thumbnail at a given time:
    > pymedia screenshoot frames input.mp4 --at 00:01:30
  Capture thumbnails at several timestamps:
    > pymedia screenshoot frames input.mp4 --at 00:01:30,00:05:15
  Save to a specific file:
    > pymedia screenshoot frames input.mp4 --at 00:01:30 --output thumb.jpg
"""
)


_HELP_INTERVAL = _(
    """\
Captures thumbnails at regular intervals of the video.

[bold]Examples[/bold]:
  Capture a thumbnail every second:
    > pymedia screenshoot interval input.mp4 --every 1
  Capture a thumbnail every 5 seconds within a time range:
    > pymedia screenshoot interval input.mp4 --every 5 --start 00:00:10 --end 00:01:00
  Save to a specific file:
    > pymedia screenshoot interval input.mp4 --every 5 --output thumb.jpg
"""
)


@screenshoot.command(
    help=_HELP_SCENE,
    no_args_is_help=True,
)
def scene(
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
    pipeline = ScreenshootPipeline(debug=debug)
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


@screenshoot.command(
    help=_HELP_FRAMES,
    no_args_is_help=True,
)
def frames(
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
    pipeline = ScreenshootPipeline(debug=debug)
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


@screenshoot.command(
    help=_HELP_INTERVAL,
    no_args_is_help=True,
)
def interval(
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
    pipeline = ScreenshootPipeline(debug=debug)
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
    screenshoot()
