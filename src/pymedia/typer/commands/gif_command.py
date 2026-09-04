"""Comando Typer para iniciar la generación de GIF."""

from pymedia.data.types import OverwriteMode, ScaleMode
from pymedia.locales import _  # noqa
from pymedia.pipeline.gif_pipeline import GifPipeline
from pymedia.typer.instance import typer_instance
from pymedia.typer.options import (
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

_HELP = _(
    """\
Generates an animated GIF from the specified video.

[bold]Examples[/bold]:
  Convert a video to GIF:   
    > pymedia gif input.mp4
  Convert a time range:     
    > pymedia gif input.mp4 --start 00:00:05 --end 00:00:12
  Set size and frame rate:  
    > pymedia gif input.mp4 --size 480x270 --fps 15
  Save to a specific file:  
    > pymedia gif input.mp4 --output output.gif
"""
)


@typer_instance.command(
    help=_HELP,
    no_args_is_help=True,
)
def gif(
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
    help_: HelpOption = False,  # noqa
) -> None:
    """Punto de entrada y desarrollo del pipeline.

    Args:
        input_single: Ruta del fichero de vídeo a procesar.
        output: Ruta absoluta del fichero de salida procesado.
        overwrite: Política ante conflicto de salida ya existente.
        timestamp_start: Marca de tiempo que indica el punto inicial.
        timestamp_end: Marca de tiempo que indica el punto final.
        fps: Imágenes por segundo del GIF.
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
    pipeline = GifPipeline(debug=debug)
    pipeline.process_parameters(
        input_single=input_single,
        output=output,
        overwrite=overwrite,
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
    )
    if not pipeline.resolve_overwrite():
        return
    pipeline.process_cmd()
