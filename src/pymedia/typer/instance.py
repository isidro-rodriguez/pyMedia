"""Instancia de Typer y sus comandos."""

import typer

from pymedia.locales import _  # noqa
from pymedia.typer.options import HelpOption

typer_instance = typer.Typer(
    name="pyMedia",
    rich_markup_mode="rich",
    no_args_is_help=True,
    add_completion=False,
)

_HELP = _(
    """\
Easy CLI for ffmpeg.

[bold]Examples[/bold]:
  Generate an animated GIF from a video:   
    > pymedia gif input.mp4
  Print GIF's help:     
    > pymedia gif --help
"""
)


@typer_instance.callback(help=_HELP)
def main(
    help_: HelpOption = False,  # noqa
) -> None:
    """Muestra la ayuda global de la aplicación cuando se invoca con `--help`."""
    pass
