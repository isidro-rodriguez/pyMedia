"""Comando Typer para iniciar la generación de GIF."""

import typer

from pymedia.pipeline.gif_pipeline import GifPipeline
from pymedia.typer.help import ANIMATED_HELP
from pymedia.typer.options import (
    CropOption,
    DebugOption,
    FlipHorizontalOption,
    FlipVerticalOption,
    FpsGifOption,
    HelpOption,
    MediaInputArgument,
    OutputOption,
    OverwriteOption,
    RotateOption,
    ScaleModeOption,
    ScaleToOption,
    ScaleUpscaleOption,
    TimestampEndGifOption,
    TimestampStartGifOption,
)
from pymedia.types import OverwriteMode, ScaleMode

gif_typer = typer.Typer()


@gif_typer.command(
    name="animated",
    help=ANIMATED_HELP,
    rich_help_panel="Image commands",
    no_args_is_help=True,
)
def gif(
    media_input: MediaInputArgument,
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
        media_input: Ruta del fichero de vídeo a procesar.
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
        media_input=media_input,
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
