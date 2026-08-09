from pathlib import Path

import typer

from pymedia.cli_params import (
    CropOption,
    EndPointOption,
    FpsOption,
    GyrateOption,
    OutputOption,
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
from pymedia.models.arguments import Arguments, CommandName
from pymedia.models.errors import InsufficientInputError

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
    inputs: PathsArgument,
    crop: CropOption = None,
    gyrate: GyrateOption = None,
    output: OutputOption = None,
    remux: RemuxOption = False,
    scale: ScaleOption = None,
) -> None:
    """Une los vídeos en el orden aportado"""
    if len(inputs) < 2:
        raise InsufficientInputError()

    concat_command(
        Arguments(
            command=CommandName.CONCAT,
            inputs=inputs,
            crop=crop,
            gyrate=gyrate,
            output=output,
            remux=remux,
            scale=scale,
        )
    )


@app.command()
def encode(
    inputs: PathsArgument,
    crop: CropOption = None,
    scale: ScaleOption = None,
    gyrate: GyrateOption = None,
    remux: RemuxOption = False,
    output: OutputOption = None,
) -> None:
    """
    Transcodifica con las opciones elegidas (requiere al menos una opción)
    """
    if crop is None and scale is None and gyrate is None and remux is False:
        logger.warning("Se requiere al menos una opción.")
        return

    encode_command(
        Arguments(
            command=CommandName.ENCODE,
            inputs=inputs,
            crop=crop,
            gyrate=gyrate,
            output=output,
            remux=remux,
            scale=scale,
        )
    )


@app.command()
def split(
    input_single: PathArgument,
    trim_points: TrimPointsOption,
    crop: CropOption = None,
    scale: ScaleOption = None,
    gyrate: GyrateOption = None,
    remux: RemuxOption = False,
    output: OutputOption = None,
) -> None:
    """Separa un vídeo en los puntos de corte indicados"""
    split_command(
        Arguments(
            command=CommandName.SPLIT,
            inputs=[input_single],
            trim_points=trim_points,
            crop=crop,
            gyrate=gyrate,
            output=output,
            remux=remux,
            scale=scale,
        )
    )


@app.command()
def gif(
    input_single: Path,
    crop: CropOption = None,
    end_point: EndPointOption = None,
    fps: FpsOption = 15,
    start_point: StartPointOption = None,
    gyrate: GyrateOption = None,
    output: OutputOption = None,
    scale: ScaleGifOption = ScaleGifMode.P480,
) -> None:
    """Genera un gif animado del vídeo aportado"""
    gif_command(
        Arguments(
            command=CommandName.GIF,
            inputs=[input_single],
            end_point=end_point,
            fps=fps,
            crop=crop,
            gyrate=gyrate,
            start_point=start_point,
            output=output,
            scale=scale,
        )
    )


if __name__ == "__main__":
    app()
