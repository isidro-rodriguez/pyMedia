# pyMedia
# > pymedia                     # Abre TUI
# > pymedia path              # Abre TUI con path cargados
# > pymedia --help              # Muestra ayuda CLI con Typer
# > pymedia ACTIONS path      # Genera comando ffmpeg y lo ejecuta por CLI
# > pymedia OPERATION ACTIONS path
from pathlib import Path
from typing import Annotated

import typer

from pymedia.domain.config import Config

app = typer.Typer()


@app.callback(invoke_without_command=True)
@app.command()
def tui(ctx: typer.Context) -> None:
    """Lanza la interfaz de usuario en terminal"""
    if ctx.invoked_subcommand is None:
        print("Lanzando TUI.")


@app.command()
def encode(
    path: list[Path],
    scale: Annotated[
        int, typer.Option("--scale", "-s", help="Redimensiona vídeo.")
    ] = 0,
    crop: Annotated[str, typer.Option("--crop", "-c", help="Recorta la imagen.")] = "",
    rotate: Annotated[int, typer.Option("--rotate", "-g", help="Gira el vídeo.")] = 0,
    transcode: Annotated[
        bool, typer.Option("--transcode", "-t", help="Transcodifica el vídeo.")
    ] = False,
) -> None:
    """Recodifica los vídeos basándose en las acciones propuestas"""
    if scale:
        print(f"Redimensionando {path} a {scale}")
    if crop:
        print(f"Cortando {path} a {crop}")
    if rotate:
        print(f"Rotando {path}: {rotate}º")
    if transcode:
        print(f"Recodificando {path}")
    config = Config.load()


@app.command()
def join(path: Path) -> None:
    """Une los vídeos en el orden aportado"""
    print("Unión")
    # TODO: implementar join


@app.command()
def split(path: Path) -> None:
    """Separa un vídeo en los puntos de corte indicados"""
    print("División")
    # TODO: implementar split


@app.command()
def gif(path: Path) -> None:
    """Genera un gif animado del vídeo aportado"""
    print("Animando gif")
    # TODO: implementar gif


@app.command()
def config() -> None:
    """Accede a la configuración de pyMedia"""
    print("Editando configuración")
    # TODO: implementar edición del config


if __name__ == "__main__":
    app()
