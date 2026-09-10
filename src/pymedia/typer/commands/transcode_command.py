"""Compositor de comandos ffmpeg para la transcodificación de vídeos."""

import typer

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
    """Comando para componer la llamada ffmpeg de transcodificación de vídeos."""
    validate_conflict_output_options(
        media_input_list=media_input_list,
        output=media_output,
        output_directory=output_directory,
    )
    for media_input in media_input_list:
        pipeline = TranscodePipeline(debug=debug)
        pipeline.process_parameters(
            media_input=media_input,
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
        if not pipeline.resolve_overwrite():
            return
        pipeline.process_cmd()
