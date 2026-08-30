from pathlib import Path
from typing import Annotated

import typer

from pymedia.locales import _  # noqa
from pymedia.models.enums import (
    OverwriteMode,
    PresetsSheetMode,
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
        "--debug",
        help=_("Log level DEBUG"),
    ),
]


HelpOption = Annotated[
    bool,
    typer.Option(
        "--help",
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


FpsGifOption = Annotated[
    int,
    typer.Option(
        "--fps",
        min=4,
        max=20,
        rich_help_panel=_("Command options"),
        help=_("Frames per second of the animated GIF."),
    ),
]


PresetSheetOption = Annotated[
    PresetsSheetMode,
    typer.Option(
        "--preset",
        rich_help_panel=_("Command options"),
        help=_("Preset sheet style."),
    ),
]

ScaleModeOption = Annotated[
    ScaleMode,
    typer.Option(
        "--mode",
        rich_help_panel=_("Command options"),
        help=_("Specify different ways to scale the video."),
    ),
]


ScaleToOption = Annotated[
    str | None,
    typer.Option(
        "--size",
        metavar="WIDTHxHEIGHT",
        rich_help_panel=_("Command options"),
        help=_("Target resolution, in pixels, to resize the video."),
    ),
]


ScaleUpscaleOption = Annotated[
    bool,
    typer.Option(
        "--upscale",
        rich_help_panel=_("Command options"),
        help=_("Allows upscaling beyond the source dimensions."),
    ),
]


TimestampEndOption = Annotated[
    str | None,
    typer.Option(
        "--end",
        metavar="hh:mm:ss",
        rich_help_panel=_("Command options"),
        help=_("Time point at which GIF generation ends."),
    ),
]


TimestampStartOption = Annotated[
    str | None,
    typer.Option(
        "--start",
        metavar="hh:mm:ss",
        rich_help_panel=_("Command options"),
        help=_("Time point at which GIF generation starts."),
    ),
]
