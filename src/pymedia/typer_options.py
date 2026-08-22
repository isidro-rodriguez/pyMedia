from pathlib import Path
from typing import Annotated

import typer

from pymedia import locales
from pymedia.models.enums import (
    OutputOnConflictMode,
)


def _show_help(ctx: typer.Context, value: bool) -> None:
    """Callback para mostar el texto de ayuda en múltiples idiomas."""
    if value:
        typer.echo(ctx.get_help())
        raise typer.Exit()


def _validate_path(path: Path) -> Path:
    """Valida la ruta indicada."""
    if not path.is_file():
        raise typer.BadParameter(locales.Cli["invalid_path"].format(path=path))
    return path


# -----------------------------------------------------------------------------
#  Argumentos
# -----------------------------------------------------------------------------


PathArgument = Annotated[
    Path,
    typer.Argument(
        help=locales.Cli["path_argument_help"],
        callback=_validate_path,
    ),
]


# -----------------------------------------------------------------------------
#  Opciones de aplicación
# -----------------------------------------------------------------------------


DebugOption = Annotated[
    bool,
    typer.Option(
        "--debug",
        help=locales.Cli["debug_help"],
    ),
]


HelpOption = Annotated[
    bool,
    typer.Option(
        "--help",
        help=locales.Cli["show_help"],  # tu texto traducido
        callback=_show_help,
        is_eager=True,
        expose_value=False,
    ),
]


# -----------------------------------------------------------------------------
#  Opciones de salida
# -----------------------------------------------------------------------------


OutputOnConflictOption = Annotated[
    OutputOnConflictMode | None,
    typer.Option(
        "--on-conflict",
        "-oc",
        rich_help_panel="Output options",
        help=locales.Cli["output_on_conflict_help"],
    ),
]


OutputOption = Annotated[
    Path | None,
    typer.Option(
        "--output",
        "-o",
        rich_help_panel="Output options",
        help=locales.Cli["output_help"],
    ),
]


# -----------------------------------------------------------------------------
#  Opciones de comando
# -----------------------------------------------------------------------------


EndPointOption = Annotated[
    str | None,
    typer.Option(
        "--end-point",
        "-ep",
        metavar="hh:mm:ss",
        rich_help_panel="Encode options",
        help=locales.Cli["end_point_help"],
    ),
]


FpsOption = Annotated[
    int | None,
    typer.Option(
        "--fps",
        "-f",
        min=4,
        max=20,
        rich_help_panel="Encode options",
        help=locales.Cli["fps_help"],
    ),
]


ScaleOption = Annotated[
    int | None,
    typer.Option(
        "--scale",
        "-s",
        min=240,
        max=2160,
        rich_help_panel="Encode options",
        help=locales.Cli["scale_help"],
    ),
]


StartPointOption = Annotated[
    str | None,
    typer.Option(
        "--start-point",
        "-sp",
        metavar="hh:mm:ss",
        rich_help_panel="Encode options",
        help=locales.Cli["start_point_help"],
    ),
]
