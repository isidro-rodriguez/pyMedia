from pathlib import Path

import typer

from pymedia import locales


def show_help(ctx: typer.Context, value: bool) -> None:
    """Callback para mostar el texto de ayuda en múltiples idiomas."""
    if value:
        typer.echo(ctx.get_help())
        raise typer.Exit()


def validate_path(path: Path) -> Path:
    """Valida la ruta indicada."""
    if not path.is_file():
        raise typer.BadParameter(locales.Cli["invalid_path"].format(path=path))
    return path
