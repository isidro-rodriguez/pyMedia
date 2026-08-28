import io
import sys

import typer

from pymedia.commands import register_all
from pymedia.services.locale_service import detect_language, set_language

# Cargar el idioma ANTES de importar typer_options (que usa locales en los help=)
set_language(detect_language())

from pymedia.typer_options import (  # noqa: E402
    HelpOption,
)

app = typer.Typer(
    name="pyMedia",
    rich_markup_mode="rich",
    no_args_is_help=True,
    add_completion=False,
)


@app.callback()
def main(
    help_: HelpOption = False,
) -> None:
    pass


if sys.platform == "win32" and isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding="utf-8")

register_all(app)


if __name__ == "__main__":
    app()
