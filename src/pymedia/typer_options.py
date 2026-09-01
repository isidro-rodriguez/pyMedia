from pathlib import Path
from typing import Annotated

import typer

from pymedia.locales import _  # noqa
from pymedia.models.enums import (
    OverwriteMode,
    PresetsSheetMode,
    RotateMode,
    ScaleMode,
)

# =============================================================================
#  Callbacks
# =============================================================================


def _show_help(ctx: typer.Context, value: bool) -> None:
    """Callback para mostar el texto de ayuda en múltiples idiomas."""
    if value:
        typer.echo(ctx.get_help())
        raise typer.Exit()


def _validate_path(path: Path) -> Path:
    """Valida la ruta indicada."""
    if not path.is_file():
        raise typer.BadParameter(_("%(path)s is not a file.") % {"path": path})
    return path


def _validate_path_list(paths: list[Path]) -> list[Path]:
    """Valida la ruta indicada."""
    for p in paths:
        if not p.is_file():
            raise typer.BadParameter(_("%(path)s is not a file.") % {"path": p})
    return paths


# =============================================================================
#  Argumentos
# =============================================================================


InputSingleArgument = Annotated[
    Path,
    typer.Argument(
        help=_("Video to process."),
        callback=_validate_path,
    ),
]

InputListArgument = Annotated[
    list[Path],
    typer.Argument(
        help=_("Video list to process."),
        callback=_validate_path_list,
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
        callback=_show_help,
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


CropOption = Annotated[
    str | None,
    typer.Option(
        default="--crop",
        metavar="WIDTH,HEIGHT,X,Y",
        rich_help_panel=_("Command options"),
        help=_("Crop to WIDTH×HEIGHT at offset X,Y (from top-left)."),
    ),
]

EveryOption = Annotated[
    int | None,
    typer.Option(
        default="--every",
        rich_help_panel=_("Command options"),
        help=_("Interval between thumbnails, in seconds."),
    ),
]

FlipHorizontalOption = Annotated[
    bool,
    typer.Option(
        default="--hflip",
        rich_help_panel=_("Command options"),
        help=_("Flip the image horizontally, swapping left and right."),
    ),
]

FlipVerticalOption = Annotated[
    bool,
    typer.Option(
        default="--vflip",
        rich_help_panel=_("Command options"),
        help=_("Flip the image vertically, swapping top and bottom."),
    ),
]


FpsGifOption = Annotated[
    int,
    typer.Option(
        default="--fps",
        min=4,
        max=20,
        rich_help_panel=_("Command options"),
        help=_("Set the GIF frame rate in frames per second."),
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

RotateOption = Annotated[
    RotateMode | None,
    typer.Option(
        default="--rotate",
        rich_help_panel=_("Command options"),
        help=_("Specify an orthogonal arc degree to rotate the image."),
    ),
]

ScaleModeOption = Annotated[
    ScaleMode,
    typer.Option(
        default="--mode",
        rich_help_panel=_("Command options"),
        help=_("Specify different ways to scale the video."),
    ),
]


ScaleToOption = Annotated[
    str | None,
    typer.Option(
        default="--size",
        metavar="WIDTHxHEIGHT",
        rich_help_panel=_("Command options"),
        help=_("Target resolution, in pixels, to resize the video."),
    ),
]


ScaleUpscaleOption = Annotated[
    bool,
    typer.Option(
        default="--upscale",
        rich_help_panel=_("Command options"),
        help=_("Allows upscaling beyond the source dimensions."),
    ),
]


SceneOption = Annotated[
    float | None,
    typer.Option(
        default="--scene",
        min=0.1,
        max=0.9,
        rich_help_panel=_("Command options"),
        help=_("Scene-change sensitivity for thumbnail detection."),
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

TimestampEndGifOption = Annotated[
    str | None,
    typer.Option(
        default="--end",
        metavar="hh:mm:ss",
        rich_help_panel=_("Command options"),
        help=_("Time point at which GIF generation ends."),
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


TimestampStartGifOption = Annotated[
    str | None,
    typer.Option(
        default="--start",
        metavar="hh:mm:ss",
        rich_help_panel=_("Command options"),
        help=_("Time point at which GIF generation starts."),
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
