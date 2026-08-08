from pathlib import Path

import typer

from pymedia.cli_params import (
    CropOption,
    EndPointOption,
    FpsOption,
    GyrateOption,
    OutputNameOption,
    PathArgument,
    PathsArgument,
    RemuxOption,
    ScaleGifMode,
    ScaleGifOption,
    ScaleOption,
    StartPointOption,
    TrimPointsOption,
)
from pymedia.commands.concat_command import concat_command
from pymedia.commands.encode_command import encode_command
from pymedia.commands.gif_command import gif_command
from pymedia.commands.split_command import split_command
from pymedia.logger import get_logger
from pymedia.models.video_pipeline import VideoPipeline

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
    pipeline = VideoPipeline.load(crop, gyrate, remux, scale)
    concat_command(paths, pipeline, output_name)


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
    pipeline = VideoPipeline.load(crop, gyrate, remux, scale)
    encode_command(paths, pipeline, output_name)


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
    pipeline = VideoPipeline.load(crop, gyrate, remux, scale)
    split_command(path, trim_points, pipeline, output_name)


@app.command()
def gif(
    path: Path,
    fps: FpsOption = 15,
    scale: ScaleGifOption = ScaleGifMode.P480,
    start_point: StartPointOption = None,
    end_point: EndPointOption = None,
    crop: CropOption = None,
    gyrate: GyrateOption = None,
    output_name: OutputNameOption = None,
) -> None:
    """Genera un gif animado del vídeo aportado"""
    pipeline = VideoPipeline.load(crop, gyrate, False, scale)
    gif_command(path, pipeline, fps, start_point, end_point, output_name)


if __name__ == "__main__":
    app()
