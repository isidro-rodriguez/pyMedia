"""Comando ``transcode``: cli."""

import typer

from pymedia.commands.base_cli import validate_conflict_output_options
from pymedia.commands.base_cli_options import (
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
    ShowCmdOption,
    TranscodeAudioOption,
    TranscodeBurnSubtitlesOption,
    TranscodeVideoOption,
)
from pymedia.commands.transcode.parameters import TranscodeParameters
from pymedia.commands.transcode.service import TranscodeService
from pymedia.errors import MissingRequiredOptionsError
from pymedia.locales import _
from pymedia.logger import Logger
from pymedia.types import OverwriteMode, PresetsTranscodeMode, ScaleMode

transcode_cli = typer.Typer()

TRANSCODE_HELP = _(
    """\
Transcode video container changing its codecs and compression.

It also allows video operations that requires transcoding.
NOTE: You can edit preset profiles in config.toml.

[bold]Examples[/bold]:
    Transcode only video track changing with a configurated profile:
    > pymedia transcode source.mp4 --preset even --video -o target.mp4
    Transcode video track meanwhile its applied multiple filters:
    > pymedia transcode source.mp4 --profile fast --size 1280x720 --hflip
    Burn subtitles in video track.
    > pymedia transcode source.mp4 --burn-subtitles eng-subs.srt
"""
)


@transcode_cli.command(
    name="transcode",
    help=TRANSCODE_HELP,
    rich_help_panel=_("Video commands"),
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
    show_cmd: ShowCmdOption = False,
    help_: HelpOption = False,
) -> None:
    """Punto de entrada del comando ``transcode``.

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
        show_cmd: Muestra al usuario el comando ffmpeg compuesto pero no lo ejecuta.
        help_: Helper para mostrar esta línea en distintos idiomas.

    Raises:
        MissingRequiredOptionsError: Si no se aporta ninguna opción de
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

    Logger.create(debug=debug)
    for media_input in media_input_list:
        params = TranscodeParameters.load(
            overwrite=overwrite,
            media_input=media_input,
            preset_transcode=preset_transcode,
            output=media_output,
            output_directory=output_directory,
            transcode_audio=transcode_audio,
            transcode_video=transcode_video,
            subtitles_input=subtitles_input,
            crop=crop,
            scale_to=scale_to,
            scale_mode=scale_mode,
            scale_upscale=scale_upscale,
            rotate=rotate,
            hflip=hflip,
            vflip=vflip,
        )
        TranscodeService(debug=debug, show_cmd=show_cmd, params=params).start()
