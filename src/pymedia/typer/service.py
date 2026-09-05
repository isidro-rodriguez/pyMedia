"""Módulo para servicios auxiliares de Typer."""

from pathlib import Path

import typer

from pymedia.errors import ExclusiveOptionsError, OptionError
from pymedia.locales import _  # noqa


def show_help(ctx: typer.Context, value: bool) -> None:
    """Muestra el texto de ayuda del comando en el idioma activo."""
    if value:
        typer.echo(ctx.get_help())
        raise typer.Exit()


def validate_conflict_output_options(
    media_input_list: list[Path], output: Path | None, output_directory: Path | None
) -> None:
    """Comprueba que no se han aportado combinaciones de opciones de salida ambiguas.

    Args:
        media_input_list: Lista de rutas de los ficheros de vídeo a procesar.
        output: Ruta absoluta del fichero de salida procesado.
        output_directory: Directorio de salida para lotes de ficheros.

    """
    if output is not None and output_directory is not None:
        raise ExclusiveOptionsError(options=["output", "output_directory"])
    if output is not None and len(media_input_list) > 1:
        raise OptionError(
            msg=_(
                "It is not allowed to specify an output with multiple inputs, "
                "use output directory instead."
            )
        )


def validate_path(path: Path) -> Path:
    """Valida la ruta indicada."""
    if not path.is_file():
        raise typer.BadParameter(_("%(path)s is not a file.") % {"path": path})
    return path


def validate_path_list(paths: list[Path]) -> list[Path]:
    """Valida la ruta indicada."""
    for p in paths:
        if not p.is_file():
            raise typer.BadParameter(_("%(path)s is not a file.") % {"path": p})
    return paths
