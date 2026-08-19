# ruff: noqa
from pathlib import Path

from dataclasses import fields

import typer

from pymedia.models.config import Config
from pymedia.services.locale_service import detect_language, set_language
from pymedia import locales

# Cargar el idioma ANTES de importar cli_params (que usa locales en los help=)
set_language(detect_language())

from pymedia.typer_options import (
    CropOption,
    DebugOption,
    EndPointOption,
    FpsOption,
    GyrateOption,
    HelpOption,
    OutputOnConflictMode,
    OutputOnConflictOption,
    OutputOption,
    InputOption,
    InputsOption,
    RemuxOption,
    ScaleGifMode,
    ScaleGifOption,
    ScaleVideoOption,
    StartPointOption,
    TrimPointsOption,
)
from pymedia.commands.concat_command import concat_command
from pymedia.commands.encode_command import encode_command
from pymedia.commands.gif_command import gif_command
from pymedia.commands.split_command import split_command
from pymedia.errors import InsufficientInputError, MissingOptionsError
from pymedia.models.arguments import Arguments
from pymedia.models.gif_parameters import GifParameters
from pymedia.models.split_parameters import SplitParameters

app = typer.Typer(
    name="pyMedia",
    rich_markup_mode="rich",
    no_args_is_help=True,
    add_completion=False,
)


def _build_arguments(local_vars: dict) -> Arguments:
    """Recoge todos los argumentos de las llamadas a comandos."""
    valid = {f.name for f in fields(Arguments)}
    return Arguments(**{k: v for k, v in local_vars.items() if k in valid})


@app.callback()
def main(
    help_: HelpOption = False,
) -> None:
    pass


@app.command(help=locales.Cli["concat_help"])
def concat(
    inputs: InputsOption,
    crop: CropOption = None,
    debug: DebugOption = False,
    gyrate: GyrateOption = None,
    help_: HelpOption = False,
    output: OutputOption = None,
    output_on_conflict: OutputOnConflictOption = OutputOnConflictMode.FAIL,
    remux: RemuxOption = False,
    scale: ScaleVideoOption = None,
) -> None:
    if len(inputs) < 2:
        raise InsufficientInputError()

    concat_command(_build_arguments(locals()))


@app.command(help=locales.Cli["encode_help"])
def encode(
    inputs: InputsOption,
    crop: CropOption = None,
    debug: DebugOption = False,
    gyrate: GyrateOption = None,
    help_: HelpOption = False,
    output: OutputOption = None,
    output_on_conflict: OutputOnConflictOption = OutputOnConflictMode.FAIL,
    remux: RemuxOption = False,
    scale: ScaleVideoOption = None,
) -> None:
    if crop is None and scale is None and gyrate is None and remux is False:
        raise MissingOptionsError()

    args = _build_arguments(locals())
    encode_command(args)


@app.command(help=locales.Cli["split_help"])
def split(
    input_single: InputOption,
    trim_points: TrimPointsOption,
    debug: DebugOption = False,
    crop: CropOption = None,
    gyrate: GyrateOption = None,
    help_: HelpOption = False,
    output: OutputOption = None,
    output_on_conflict: OutputOnConflictOption = OutputOnConflictMode.FAIL,
    remux: RemuxOption = False,
    scale: ScaleVideoOption = None,
) -> None:
    config = Config.load()

    split_command(
        SplitParameters(
            args=_build_arguments(locals()),
            config=config,
        ),
        config=config,
    )


@app.command(help=locales.Cli["gif_help"])
def gif(
    input_single: InputOption,
    debug: DebugOption = False,
    crop: CropOption = None,
    end_point: EndPointOption = None,
    fps: FpsOption = 15,
    gyrate: GyrateOption = None,
    help_: HelpOption = False,
    output: OutputOption = None,
    output_on_conflict: OutputOnConflictOption = OutputOnConflictMode.FAIL,
    scale: ScaleGifOption = ScaleGifMode.P480,
    start_point: StartPointOption = None,
) -> None:

    gif_command(
        GifParameters(
            args=_build_arguments(locals()),
            config=Config.load(),
        )
    )


if __name__ == "__main__":
    app()
