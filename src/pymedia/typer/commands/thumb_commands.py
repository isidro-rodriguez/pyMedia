"""Comandos de la familia thumbnails."""

import typer

from pymedia.pipeline.thumb_pipeline import ThumbPipeline
from pymedia.typer.help import (
    THUMB_FRAMES_HELP,
    THUMB_INTERVAL_HELP,
    THUMB_SCENE_HELP,
)
from pymedia.typer.options import (
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
    SceneOption,
    TimestampAtThumbnailOption,
    TimestampEndGifOption,
    TimestampStartGifOption,
)
from pymedia.types import OverwriteMode, ScaleMode

thumb_typer = typer.Typer()

# =============================================================================
#  Subcomando FRAMES
# =============================================================================


@thumb_typer.command(
    name="frames",
    help=THUMB_FRAMES_HELP,
    rich_help_panel="Image commands",
    no_args_is_help=True,
)
def frames(
    media_input: MediaInputArgument,
    output: OutputOption = None,
    overwrite: OverwriteOption = OverwriteMode.YES,
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
    """
    pipeline = ThumbPipeline(debug=debug)
    pipeline.process_parameters(
        media_input=media_input,
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


@thumb_typer.command(
    name="interval",
    help=THUMB_INTERVAL_HELP,
    rich_help_panel="Image commands",
    no_args_is_help=True,
)
def interval(
    media_input: MediaInputArgument,
    output: OutputOption = None,
    overwrite: OverwriteOption = OverwriteMode.YES,
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
    """
    pipeline = ThumbPipeline(debug=debug)
    pipeline.process_parameters(
        media_input=media_input,
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
    thumb_typer()

# =============================================================================
#  Subcomando SCENE
# =============================================================================


@thumb_typer.command(
    name="scene",
    help=THUMB_SCENE_HELP,
    rich_help_panel="Image commands",
    no_args_is_help=True,
)
def scene(
    media_input: MediaInputArgument,
    output: OutputOption = None,
    overwrite: OverwriteOption = OverwriteMode.YES,
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
        help_: Helper para mostrar esta línea en distintos idiomas.
    """
    pipeline = ThumbPipeline(debug=debug)
    pipeline.process_parameters(
        media_input=media_input,
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
