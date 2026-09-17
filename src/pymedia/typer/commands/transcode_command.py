"""Compositor de comandos ffmpeg para la transcodificación de vídeos."""

import typer

from pymedia.errors import MissingRequiredOptionsError
from pymedia.locales import _  # noqa
from pymedia.pipeline.transcode_pipeline import TranscodePipeline
from pymedia.typer.help import TRANSCODE_HELP
from pymedia.typer.options import (
    CropOption,
    DebugOption,
    FlipHorizontalOption,
    FlipVerticalOption,
    HelpOption,
    MediaInputListArgument,
    OutputDirectoryOption,
    OutputOption,
    OverwriteOption,
    PresetsTranscodeOption,
    RotateOption,
    ScaleModeOption,
    ScaleToOption,
    ScaleUpscaleOption,
    TranscodeAudioOption,
    TranscodeBurnSubtitlesOption,
    TranscodeVideoOption,
)
from pymedia.typer.service import validate_conflict_output_options
from pymedia.types import OverwriteMode, PresetsTranscodeMode, ScaleMode

transcode_typer = typer.Typer()


@transcode_typer.command(
    name="transcode",
    help=TRANSCODE_HELP,
    rich_help_panel="Video commands",
    no_args_is_help=True,
)
def transcode(
    media_input_list: MediaInputListArgument,
    media_output: OutputOption = None,
    output_directory: OutputDirectoryOption = None,
    overwrite: OverwriteOption = OverwriteMode.ASK,
    preset_transcode: PresetsTranscodeOption = PresetsTranscodeMode.EVEN,
    transcode_audio: TranscodeAudioOption = None,
    subtitles_input: TranscodeBurnSubtitlesOption = None,
    transcode_video: TranscodeVideoOption = False,
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
    """Comando para componer la llamada ffmpeg de transcodificación de vídeos.

    Args:
        media_input_list: Lista de rutas de los ficheros de vídeo a procesar.
        media_output: Ruta absoluta del fichero de salida procesado.
        output_directory: Directorio de salida para lotes de ficheros.
        overwrite: Política ante conflicto de salida ya existente.
        preset_transcode: Perfil de transcodificación de config.toml.
        transcode_audio: Lista de pistas de audio a transcodificar.
        subtitles_input: Subtítulos a quemar en la pista de vídeo.
        transcode_video: Transcodifica la pista de vídeo.
        crop: Área y coordenada de la zona a preservar de la imagen.
        rotate: Ángulo ortogonal con el que se va a rotar la imagen.
        scale_to: Dimensión objetivo en píxeles.
        scale_mode: Política de escalado del vídeo o imagen.
        scale_upscale: Permite el incremento de dimensiones.
        hflip: Invierte la imagen horizontalmente.
        vflip: Invierte la imagen verticalmente.
        debug: Habilita el nivel de log DEBUG.
        help_: Helper para mostrar esta línea en distintos idiomas.

    Raises:
        MissingRequiredOptionError: Si no se aporta ninguna opción de
            transcodificación.
    """
    if (
        transcode_audio is None
        and transcode_video is False
        and subtitles_input is None
        and crop is None
        and rotate is None
        and scale_to is None
        and hflip is False
        and vflip is False
    ):
        raise MissingRequiredOptionsError(
            options=[
                "audio",
                "video",
                "burn-subtitles",
                "crop",
                "rotate",
                "scale_to",
                "hflip",
                "vflip",
            ]
        )

    validate_conflict_output_options(
        media_input_list=media_input_list,
        output=media_output,
        output_directory=output_directory,
    )

    for media_input in media_input_list:
        pipeline = TranscodePipeline(debug=debug)
        pipeline.process_parameters(
            media_input=media_input,
            subtitles_input=subtitles_input,
            overwrite=overwrite,
            preset_transcode=preset_transcode,
            scale_mode=scale_mode,
            output=media_output,
            output_directory=output_directory,
            transcode_audio=transcode_audio,
            transcode_video=transcode_video,
            crop=crop,
            scale_to=scale_to,
            scale_upscale=scale_upscale,
            rotate=rotate,
            hflip=hflip,
            vflip=vflip,
        )
        pipeline.process_cmd()
