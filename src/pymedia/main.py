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
from pymedia.commands.concat_command import concat_command
from pymedia.commands.encode_command import encode_command
from pymedia.commands.split_command import split_command
from pymedia.domain.encode_pipeline import EncodePipeline
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
def concat(
    paths: PathsArgument,
    crop: CropOption = None,
    scale: ScaleOption = None,
    gyrate: GyrateOption = None,
    remux: RemuxOption = False,
    output_name: OutputNameOption = None,
) -> None:
    """Une los vídeos en el orden aportado"""
    if len(paths) < 2:
        logger.warning("Se requiere al menos dos vídeos.")
        return
    pipeline = EncodePipeline.load(crop=crop, gyrate=gyrate, remux=remux, scale=scale)
    concat_command(paths, pipeline, output_name=output_name)


@app.command()
def encode(
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
    pipeline = EncodePipeline.load(crop=crop, gyrate=gyrate, remux=remux, scale=scale)
    encode_command(paths, pipeline, output_name=output_name)


@app.command()
def split(
    trim_points: TrimPointsOption,
    path: PathArgument,
    crop: CropOption = None,
    scale: ScaleOption = None,
    gyrate: GyrateOption = None,
    remux: RemuxOption = False,
    output_name: OutputNameOption = None,
) -> None:
    """Separa un vídeo en los puntos de corte indicados"""
    pipeline = EncodePipeline.load(crop=crop, gyrate=gyrate, remux=remux, scale=scale)
    split_command(path, trim_points, pipeline, output_name=output_name)


@app.command()
def gif(
    path: Path,
    output_name: OutputNameOption = None,
) -> None:
    """Genera un gif animado del vídeo aportado"""
    logger.info("Animando gif")
    # TODO: implementar gif


@app.command()
def config() -> None:
    """Accede a la configuración de pyMedia"""
    logger.info("Editando configuración")
    # TODO: implementar edición del config


if __name__ == "__main__":
    app()
