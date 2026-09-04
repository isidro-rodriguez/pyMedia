"""Índice de comandos de Typer."""

from pymedia.typer.app import app
from pymedia.typer.commands import gif_command, info_command

app = app()
app.add_typer(info_command)
app.add_typer(gif_command)
