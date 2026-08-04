from pathlib import Path

import typer

from pymedia.cli_params import (
    CropOption,
    GyrateOption,
    OutputNameOption,
    PathArgument,
    PathsArgument,
    RemuxOption,
    ScaleOption,
    TrimPointsOption,
)
from pymedia.commands.transcode import transcode
from pymedia.domain.config import Config
from pymedia.domain.transcoding_pipeline import TranscodingPipeline
from pymedia.logger import get_logger

app = typer.Typer()
logger = get_logger("main")


@app.callback(invoke_without_command=True)
@app.command()
def tui(ctx: typer.Context) -> None:
    """Lanza la interfaz de usuario en terminal"""
    if ctx.invoked_subcommand is None:
        logger.info("Lanzando TUI.")


@app.command()
def recode(
    paths: PathsArgument,
    crop: CropOption = None,
    scale: ScaleOption = None,
    gyrate: GyrateOption = None,
    remux: RemuxOption = False,
    output_name: OutputNameOption = None,
) -> None:
    """
    Transcodifica con las opciones elegidas (requiere al menos una opción)
    """
    if crop is None and scale is None and gyrate is None and remux is False:
        logger.warning("Se requiere al menos una opción.")
        return
    pipeline = TranscodingPipeline.load(
        crop=crop, gyrate=gyrate, remux=remux, scale=scale
    )
    transcode(paths, Config.load(), pipeline, output_name=output_name)


@app.command()
def join(
    paths: PathsArgument,
    crop: CropOption = None,
    scale: ScaleOption = None,
    gyrate: GyrateOption = None,
    remux: RemuxOption = False,
) -> None:
    """Une los vídeos en el orden aportado"""
    logger.info("Unión")
    # TODO: implementar join


@app.command()
def split(
    trim_points: TrimPointsOption,
    path: PathArgument,
    crop: CropOption = None,
    scale: ScaleOption = None,
    gyrate: GyrateOption = None,
    remux: RemuxOption = False,
) -> None:
    """Separa un vídeo en los puntos de corte indicados"""
    logger.info("División")
    # TODO: implementar split


@app.command()
def gif(path: Path) -> None:
    """Genera un gif animado del vídeo aportado"""
    logger.info("Animando gif")
    # TODO: implementar gif


@app.command()
def configuration() -> None:
    """Accede a la configuración de pyMedia"""
    logger.info("Editando configuración")
    # TODO: implementar edición del config


if __name__ == "__main__":
    app()
