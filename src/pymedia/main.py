import inspect

import typer

from pymedia import locales
from pymedia.commands.gif_command import gif_command
from pymedia.logger import Logger
from pymedia.models.config import Config
from pymedia.models.gif_model import GifArguments, GifParameters
from pymedia.services.locale_service import detect_language, set_language

# Cargar el idioma ANTES de importar typer_options (que usa locales en los help=)
set_language(detect_language())

from pymedia.typer_options import (  # noqa: E402
    DebugOption,
    EndPointOption,
    FpsOption,
    HelpOption,
    OutputOnConflictMode,
    OutputOnConflictOption,
    OutputOption,
    PathArgument,
    ScaleOption,
    StartPointOption,
)


def _build_args(args_cls, local_vars: dict):
    """Recoge todos los argumentos de la lista de parámetros"""
    valid_params = inspect.signature(args_cls).parameters
    return args_cls(**{k: v for k, v in local_vars.items() if k in valid_params})


app = typer.Typer(
    name="pyMedia",
    rich_markup_mode="rich",
    no_args_is_help=True,
    add_completion=False,
)


@app.callback()
def main(
    debug: bool = False,
    help_: HelpOption = False,
) -> None:
    pass


@app.command(help=locales.Cli["gif_help"])
def gif(
    input_single: PathArgument,
    output: OutputOption = None,
    output_on_conflict: OutputOnConflictOption = OutputOnConflictMode.FAIL,
    fps: FpsOption = 15,
    scale: ScaleOption = 480,
    start_point: StartPointOption = None,
    end_point: EndPointOption = None,
    help_: HelpOption = False,
    debug: DebugOption = False,
) -> None:
    """Proceso para la ejecución del comando de generación de gifs."""
    config = Config.load()
    Logger.create(debug=debug)

    gif_command(
        config=config,
        params=GifParameters.create(
            args=_build_args(args_cls=GifArguments, local_vars=locals()),
            config=config,
        ),
    )


if __name__ == "__main__":
    app()
