from pymedia.locales import _  # noqa
from pymedia.pipeline.screenshoot_pipeline import ScreenshootPipeline
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

# TODO: retocar
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
def screenshoot(
    input_single: InputSingleArgument,
    output: OutputOption = None,
    overwrite: OverwriteOption = OverwriteMode.ASK,
    every: EveryOption = None,
    scene: SceneOption = None,
    timestamp_at: TimestampAtThumbnailOption = None,
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
        scene: Umbral de sensibilidad para detección de cambio de escena.
        timestamp_at: Lista de marcas de tiempo.
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
        scene=scene,
        timestamp_at=timestamp_at,
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
