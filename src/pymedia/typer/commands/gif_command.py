"""Comando Typer para iniciar la generación de GIF."""

from pymedia.data.types import OverwriteMode, ScaleMode
from pymedia.locales import _  # noqa
from pymedia.pipeline.gif_pipeline import GifPipeline
from pymedia.typer.app import app
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
  Convert a video to GIF:   > pymedia gif input.mp4
  Convert a time range:     > pymedia gif input.mp4 --start 00:00:05 --end 00:00:12
  Set size and frame rate:  > pymedia gif input.mp4 --size 480x270 --fps 15
  Save to a specific file:  > pymedia gif input.mp4 --output output.gif
"""
)


@app.command(
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
        input_single: Vídeo de entrada.
        output: Ruta de salida (por defecto, se deriva de la entrada).
        overwrite: Política ante un fichero de salida existente.
        timestamp_start: Marca temporal del punto inicial.
        timestamp_end: Marca temporal del punto final.
        fps: Imágenes por segundo del GIF.
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
