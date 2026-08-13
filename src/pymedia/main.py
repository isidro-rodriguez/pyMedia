from pathlib import Path

import typer

from pymedia.cli_params import (
    CropOption,
    DebugOption,
    EndPointOption,
    FpsOption,
    GyrateOption,
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
from pymedia.logger import setup_logging
from pymedia.models.arguments import Arguments, CommandName

app = typer.Typer(
    name="pyMedia",
    rich_markup_mode="rich",
    no_args_is_help=True,
    add_completion=False,
)


@app.callback()
def main(debug: DebugOption = False) -> None:
    setup_logging(debug=debug)


@app.command()
def concat(
    inputs: PathsArgument,
    crop: CropOption = None,
    gyrate: GyrateOption = None,
    remux: RemuxOption = False,
    scale: ScaleVideoOption = None,
    output: OutputOption = None,
    output_on_conflict: OutputOnConflictOption = OutputOnConflictMode.FAIL,
) -> None:
    """Concatenates videos in the specified order"""
    if len(inputs) < 2:
        raise InsufficientInputError()

    concat_command(
        Arguments(
            command=CommandName.CONCAT,
            inputs=inputs,
            crop=crop,
            gyrate=gyrate,
            remux=remux,
            scale=scale,
            output=output,
            output_on_conflict=output_on_conflict,
        )
    )


@app.command()
def encode(
    inputs: PathsArgument,
    crop: CropOption = None,
    debug: DebugOption = False,
    scale: ScaleVideoOption = None,
    gyrate: GyrateOption = None,
    remux: RemuxOption = False,
    output: OutputOption = None,
    output_on_conflict: OutputOnConflictOption = OutputOnConflictMode.FAIL,
) -> None:
    """
    Transcode using the selected options (requires at least one option)
    """
    if crop is None and scale is None and gyrate is None and remux is False:
        raise MissingOptionsError()

    encode_command(
        Arguments(
            command=CommandName.ENCODE,
            inputs=inputs,
            crop=crop,
            gyrate=gyrate,
            remux=remux,
            scale=scale,
            output=output,
            output_on_conflict=output_on_conflict,
        )
    )


@app.command()
def split(
    input_single: PathArgument,
    trim_points: TrimPointsOption,
    crop: CropOption = None,
    debug: DebugOption = False,
    scale: ScaleVideoOption = None,
    gyrate: GyrateOption = None,
    remux: RemuxOption = False,
    output: OutputOption = None,
    output_on_conflict: OutputOnConflictOption = OutputOnConflictMode.FAIL,
) -> None:
    """Splits a video at the specified points"""
    split_command(
        Arguments(
            command=CommandName.SPLIT,
            inputs=[input_single],
            trim_points=trim_points,
            crop=crop,
            gyrate=gyrate,
            remux=remux,
            scale=scale,
            output=output,
            output_on_conflict=output_on_conflict,
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
    output_on_conflict: OutputOnConflictOption = OutputOnConflictMode.FAIL,
) -> None:
    """Generates an animated GIF from the specified video"""
    gif_command(
        Arguments(
            command=CommandName.GIF,
            inputs=[input_single],
            end_point=end_point,
            fps=fps,
            crop=crop,
            gyrate=gyrate,
            scale=scale,
            start_point=start_point,
            output=output,
            output_on_conflict=output_on_conflict,
        )
    )


if __name__ == "__main__":
    app()
