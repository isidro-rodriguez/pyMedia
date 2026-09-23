"""Tipos `Annotated` reutilizables para las opciones y argumentos de Typer.

Agrupa las definiciones de argumentos y opciones compartidas por los subcomandos,
con textos de ayuda localizados.
"""

from pathlib import Path
from typing import Annotated

import typer

from pymedia.commands.base_cli import (
    show_help,
    show_version,
    validate_audio_path,
    validate_media_path,
    validate_media_path_list,
    validate_subtitles_path,
)
from pymedia.locales import _
from pymedia.types import (
    OverwriteMode,
    PresetsSheetMode,
    PresetsTranscodeMode,
    RotateMode,
    ScaleMode,
)

# =============================================================================
#  Argumentos
# =============================================================================

AudioArgument = Annotated[
    Path,
    typer.Argument(
        help=_("Audio track to insert in a media container."),
        metavar="AUDIO_FILE",
        callback=validate_audio_path,
    ),
]

MediaInputArgument = Annotated[
    Path,
    typer.Argument(
        help=_("Video to process."),
        metavar="MEDIA_FILE",
        callback=validate_media_path,
    ),
]

MediaInputListArgument = Annotated[
    list[Path],
    typer.Argument(
        help=_("Video list to process."),
        metavar="MEDIA_FILE MEDIA_FILE ...",
        callback=validate_media_path_list,
    ),
]

SubtitlesArgument = Annotated[
    Path,
    typer.Argument(
        help=_("Subtitles to insert in a media container."),
        metavar="SUBTITLES_FILE",
        callback=validate_subtitles_path,
    ),
]

# =============================================================================
#  Opciones de aplicación
# =============================================================================

DebugOption = Annotated[
    bool,
    typer.Option(
        default="--debug",
        help=_("Log level DEBUG"),
    ),
]

HelpOption = Annotated[
    bool,
    typer.Option(
        default="--help",
        help=_("Show this msg and exit."),
        callback=show_help,
        is_eager=True,
        expose_value=False,
    ),
]

ShowCmdOption = Annotated[
    bool,
    typer.Option(
        default="--show-cmd",
        help=_("Print the FFmpeg command without executing it."),
    ),
]

VersionOption = Annotated[
    bool,
    typer.Option(
        default="--version",
        help=_("Show version and exit."),
        callback=show_version,
        is_eager=True,
        expose_value=False,
    ),
]

# =============================================================================
#  Opciones de salida
# =============================================================================

OutputDirectoryOption = Annotated[
    Path | None,
    typer.Option(
        "--directory",
        "-d",
        rich_help_panel=_("Output options"),
        help=_("Output directory for multiple output files."),
    ),
]

OutputOption = Annotated[
    Path | None,
    typer.Option(
        "--output",
        "-o",
        rich_help_panel=_("Output options"),
        help=_("Output file name."),
    ),
]

OverwriteOption = Annotated[
    OverwriteMode,
    typer.Option(
        "--overwrite",
        "-ov",
        rich_help_panel=_("Output options"),
        help=_("Action to use if output file already exists."),
    ),
]

# =============================================================================
#  Opciones de comando
# =============================================================================

EveryOption = Annotated[
    int | None,
    typer.Option(
        default="--every",
        rich_help_panel=_("Command options"),
        help=_("Interval between thumbnails, in seconds."),
    ),
]

RegeneratePtsOption = Annotated[
    bool,
    typer.Option(
        default="--genpts",
        rich_help_panel=_("Command options"),
        help=_("Regenerates broken timestamps."),
    ),
]

PresetSheetOption = Annotated[
    PresetsSheetMode,
    typer.Option(
        default="--preset",
        rich_help_panel=_("Command options"),
        help=_("Preset sheet style."),
    ),
]

PresetsTranscodeOption = Annotated[
    PresetsTranscodeMode,
    typer.Option(
        default="--preset",
        rich_help_panel=_("Command options"),
        help=_("Transcoding profile from config.toml."),
    ),
]

SceneOption = Annotated[
    float | None,
    typer.Option(
        default="--scene",
        min=0.1,
        max=0.5,
        rich_help_panel=_("Command options"),
        help=_("Scene-change sensitivity for thumbnail detection."),
    ),
]

SortTracksOption = Annotated[
    bool,
    typer.Option(
        default="--sort-tracks",
        rich_help_panel=_("Command options"),
        help=_("Sort stream track by type and alphabetically by language."),
    ),
]

TimestampAtMediaOption = Annotated[
    str | None,
    typer.Option(
        default="--at",
        metavar="hh:mm:ss,hh:mm:ss,...",
        rich_help_panel=_("Command options"),
        help=_("Timestamps list to split a media container."),
    ),
]

TimestampEndMediaOption = Annotated[
    str | None,
    typer.Option(
        default="--end",
        metavar="hh:mm:ss",
        rich_help_panel=_("Command options"),
        help=_("Timestamp where the output media file ends."),
    ),
]

TimestampStartMediaOption = Annotated[
    str | None,
    typer.Option(
        default="--start",
        metavar="hh:mm:ss",
        rich_help_panel=_("Command options"),
        help=_("Timestamp where the output media file starts."),
    ),
]

TimestampAtThumbnailOption = Annotated[
    str | None,
    typer.Option(
        default="--at",
        metavar="hh:mm:ss,hh:mm:ss,...",
        rich_help_panel=_("Command options"),
        help=_("Take a thumbnail at specific TIMESTAMP(s)."),
    ),
]

TimestampEndAnimatedOption = Annotated[
    str | None,
    typer.Option(
        default="--end",
        metavar="hh:mm:ss",
        rich_help_panel=_("Command options"),
        help=_("Time point at which the animated image generation ends."),
    ),
]

TimestampEndThumbnailOption = Annotated[
    str | None,
    typer.Option(
        default="--end",
        metavar="hh:mm:ss",
        rich_help_panel=_("Command options"),
        help=_("Time point at which thumbnails generation ends."),
    ),
]

TimestampStartAnimatedOption = Annotated[
    str | None,
    typer.Option(
        default="--start",
        metavar="hh:mm:ss",
        rich_help_panel=_("Command options"),
        help=_("Time point at which the animated image generation starts."),
    ),
]

TimestampStartThumbnailOption = Annotated[
    str | None,
    typer.Option(
        default="--start",
        metavar="hh:mm:ss",
        rich_help_panel=_("Command options"),
        help=_("Time point at which thumbnails generation starts."),
    ),
]

TranscodeAudioOption = Annotated[
    str | None,
    typer.Option(
        default="--audio",
        metavar="int,int,...",
        rich_help_panel=_("Command options"),
        help=_("Set to transcode an audio track."),
    ),
]

TranscodeBurnSubtitlesOption = Annotated[
    Path | None,
    typer.Option(
        default="--burn-subtitles",
        rich_help_panel=_("Command options"),
        help=_("Burn subtitles file in video track."),
    ),
]

TranscodeVideoOption = Annotated[
    bool,
    typer.Option(
        default="--video",
        rich_help_panel=_("Command options"),
        help=_("Set to transcode the video track."),
    ),
]

# =============================================================================
#  Opciones de audio
# =============================================================================

AudioCommentaryOption = Annotated[
    bool | None,
    typer.Option(
        default="--commentary/--no-commentary",
        rich_help_panel=_("Audio options"),
        help=_("Set as commentary audio track."),
    ),
]

AudioDefaultOption = Annotated[
    bool | None,
    typer.Option(
        default="--default/--no-default",
        rich_help_panel=_("Audio options"),
        help=_("Set as default audio track of the container."),
    ),
]

AudioForcedOption = Annotated[
    bool | None,
    typer.Option(
        default="--forced/--no-forced",
        rich_help_panel=_("Audio options"),
        help=_("Set as forced to be displayed."),
    ),
]

AudioHearingImpairedOption = Annotated[
    bool | None,
    typer.Option(
        default="--hearing-impaired/--no-hearing-impaired",
        rich_help_panel=_("Audio options"),
        help=_("Set audio track as targeted for hearing impaired people."),
    ),
]

AudioLanguageOption = Annotated[
    str | None,
    typer.Option(
        default="--language",
        rich_help_panel=_("Audio options"),
        help=_("Set audio language, formatted as ISO 639-2 code."),
    ),
]

AudioStreamTrackListOption = Annotated[
    str | None,
    typer.Option(
        default="--tracks",
        metavar="int,int,...",
        rich_help_panel=_("Audio options"),
        help=_("List of audio tracks to process."),
    ),
]

AudioStreamTrackOption = Annotated[
    str | None,
    typer.Option(
        default="--track",
        metavar="int",
        rich_help_panel=_("Audio options"),
        help=_("Audio track to edit."),
    ),
]

AudioTitleOption = Annotated[
    str | None,
    typer.Option(
        default="--title",
        rich_help_panel=_("Audio options"),
        help=_("Set a custom audio track title for video player."),
    ),
]

# =============================================================================
#  Opciones de subtítulos
# =============================================================================

SubtitlesDefaultOption = Annotated[
    bool | None,
    typer.Option(
        default="--default/--no-default",
        rich_help_panel=_("Subtitles options"),
        help=_("Set as default subtitles of the container."),
    ),
]

SubtitlesForcedOption = Annotated[
    bool | None,
    typer.Option(
        default="--forced/--no-forced",
        rich_help_panel=_("Subtitles options"),
        help=_("Set as forced to be displayed."),
    ),
]

SubtitlesHearingImpairedOption = Annotated[
    bool | None,
    typer.Option(
        default="--hearing-impaired/--no-hearing-impaired",
        rich_help_panel=_("Subtitles options"),
        help=_("Set as targeted for hearing impaired people."),
    ),
]

SubtitlesLanguageOption = Annotated[
    str | None,
    typer.Option(
        default="--language",
        rich_help_panel=_("Subtitles options"),
        help=_("Set subtitles language, formatted as ISO 639-2 code."),
    ),
]

SubtitlesStreamTrackListOption = Annotated[
    str | None,
    typer.Option(
        default="--tracks",
        metavar="int,int,...",
        rich_help_panel=_("Subtitles options"),
        help=_("List of subtitles tracks to process."),
    ),
]

SubtitlesStreamTrackOption = Annotated[
    str | None,
    typer.Option(
        default="--track",
        metavar="int",
        rich_help_panel=_("Subtitles options"),
        help=_("Subtitles track to edit."),
    ),
]

SubtitlesTitleOption = Annotated[
    str | None,
    typer.Option(
        default="--title",
        rich_help_panel=_("Subtitles options"),
        help=_("Set a custom title for video player."),
    ),
]

SubtitlesVisualImpairedOption = Annotated[
    bool | None,
    typer.Option(
        default="--visual-impaired/--no-visual-impaired",
        rich_help_panel=_("Subtitles options"),
        help=_("Set as targeted for visual impaired people."),
    ),
]

# =============================================================================
#  Opciones de filtros
# =============================================================================

CropOption = Annotated[
    str | None,
    typer.Option(
        default="--crop",
        metavar="WIDTH,HEIGHT,X,Y",
        rich_help_panel=_("Filter options"),
        help=_("Crop to WIDTH×HEIGHT at offset X,Y (from top-left)."),
    ),
]

FlipHorizontalOption = Annotated[
    bool,
    typer.Option(
        default="--hflip",
        rich_help_panel=_("Filter options"),
        help=_("Flip the image horizontally, swapping left and right."),
    ),
]

FlipVerticalOption = Annotated[
    bool,
    typer.Option(
        default="--vflip",
        rich_help_panel=_("Filter options"),
        help=_("Flip the image vertically, swapping top and bottom."),
    ),
]

FpsAnimatedOption = Annotated[
    int,
    typer.Option(
        default="--fps",
        min=4,
        max=20,
        rich_help_panel=_("Filter options"),
        help=_("Set the animated image frame rate in frames per second."),
    ),
]

RotateOption = Annotated[
    RotateMode | None,
    typer.Option(
        default="--rotate",
        rich_help_panel=_("Filter options"),
        help=_("Specify an orthogonal arc degree to rotate the image."),
    ),
]

# =============================================================================
#  Opciones de filtros de escalado
# =============================================================================

ScaleModeOption = Annotated[
    ScaleMode,
    typer.Option(
        default="--mode",
        rich_help_panel=_("Scale filter options"),
        help=_("Specify different ways to scale the video."),
    ),
]

ScaleToOption = Annotated[
    str | None,
    typer.Option(
        default="--size",
        metavar="WIDTHxHEIGHT",
        rich_help_panel=_("Scale filter options"),
        help=_("Target resolution, in pixels, to resize the video."),
    ),
]

ScaleUpscaleOption = Annotated[
    bool,
    typer.Option(
        default="--upscale",
        rich_help_panel=_("Scale filter options"),
        help=_("Allows upscaling beyond the source dimensions."),
    ),
]
