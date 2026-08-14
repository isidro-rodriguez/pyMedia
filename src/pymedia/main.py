# ruff: noqa
from pathlib import Path

import typer

from pymedia.services.locale_service import detect_language, set_language

# Cargar el idioma ANTES de importar cli_params (que usa locales en los help=)
set_language(detect_language())

from pymedia import locales
from pymedia.cli_params import (
    CropOption,
    DebugOption,
    EndPointOption,
    FpsOption,
    GyrateOption,
    HelpOption,
    OutputOnConflictMode,
    OutputOnConflictOption,
    OutputOption,
    PathArgument,
    PathsArgument,
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
from pymedia.models.arguments import Arguments, CommandName

app = typer.Typer(
    name="pyMedia",
    rich_markup_mode="rich",
    no_args_is_help=True,
    add_completion=False,
)


@app.callback()
def main(
    debug: DebugOption = False,
    help_: HelpOption = False,
) -> None:
    pass


@app.command(help=locales.Cli["concat_help"])
def concat(
    inputs: PathsArgument,
    crop: CropOption = None,
    debug: DebugOption = False,
    gyrate: GyrateOption = None,
    help_: HelpOption = False,
    remux: RemuxOption = False,
    scale: ScaleVideoOption = None,
    output: OutputOption = None,
    output_on_conflict: OutputOnConflictOption = OutputOnConflictMode.FAIL,
) -> None:
    if len(inputs) < 2:
        raise InsufficientInputError()

    concat_command(
        Arguments(
            command=CommandName.CONCAT,
            inputs=inputs,
            crop=crop,
            gyrate=gyrate,
            output=output,
            output_on_conflict=output_on_conflict,
            remux=remux,
            scale=scale,
        )
    )


@app.command(help=locales.Cli["encode_help"])
def encode(
    inputs: PathsArgument,
    crop: CropOption = None,
    gyrate: GyrateOption = None,
    help_: HelpOption = False,
    output: OutputOption = None,
    output_on_conflict: OutputOnConflictOption = OutputOnConflictMode.FAIL,
    remux: RemuxOption = False,
    scale: ScaleVideoOption = None,
) -> None:
    if crop is None and scale is None and gyrate is None and remux is False:
        raise MissingOptionsError()

    encode_command(
        Arguments(
            command=CommandName.ENCODE,
            inputs=inputs,
            crop=crop,
            gyrate=gyrate,
            output=output,
            output_on_conflict=output_on_conflict,
            remux=remux,
            scale=scale,
        )
    )


@app.command(help=locales.Cli["split_help"])
def split(
    input_single: PathArgument,
    trim_points: TrimPointsOption,
    debug: DebugOption = False,
    help_: HelpOption = False,
    crop: CropOption = None,
    scale: ScaleVideoOption = None,
    gyrate: GyrateOption = None,
    remux: RemuxOption = False,
    output: OutputOption = None,
    output_on_conflict: OutputOnConflictOption = OutputOnConflictMode.FAIL,
) -> None:
    split_command(
        Arguments(
            command=CommandName.SPLIT,
            inputs=[input_single],
            trim_points=trim_points,
            crop=crop,
            gyrate=gyrate,
            output=output,
            output_on_conflict=output_on_conflict,
            remux=remux,
            scale=scale,
        )
    )


@app.command(help=locales.Cli["gif_help"])
def gif(
    input_single: Path,
    debug: DebugOption = False,
    help_: HelpOption = False,
    crop: CropOption = None,
    end_point: EndPointOption = None,
    fps: FpsOption = 15,
    start_point: StartPointOption = None,
    gyrate: GyrateOption = None,
    output: OutputOption = None,
    scale: ScaleGifOption = ScaleGifMode.P480,
    output_on_conflict: OutputOnConflictOption = OutputOnConflictMode.FAIL,
) -> None:
    gif_command(
        Arguments(
            command=CommandName.GIF,
            inputs=[input_single],
            crop=crop,
            end_point=end_point,
            fps=fps,
            output=output,
            output_on_conflict=output_on_conflict,
            gyrate=gyrate,
            scale=scale,
            start_point=start_point,
        )
    )


if __name__ == "__main__":
    app()
