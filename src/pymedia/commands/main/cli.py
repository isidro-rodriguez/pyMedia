"""Comando ``main``: cli."""

import shutil

from pymedia.commands.base_cli import base_cli
from pymedia.commands.base_cli_options import HelpOption, VersionOption
from pymedia.errors import UserError
from pymedia.locales import _

main_cli = base_cli

MAIN_HELP = _(
    """\
Easy CLI for ffmpeg.

[bold]Examples[/bold]:
  Show help and exit:
    > pymedia --help
    > pymedia
  Show subcommand help and exit:
    > pymedia transcode --help
    > pymedia transcode
  Show version and exit:
    > pymedia --version
"""
)


@main_cli.callback(help=MAIN_HELP)
def main(
    help_: HelpOption = False,  # noqa
    version: VersionOption = False,  # noqa
) -> None:
    """Muestra la ayuda global de la aplicación cuando se invoca con `--help`.

    Args:
        help_: Solicitud explícita de ayuda del comando.
        version: Mostrar la versión de la aplicación.

    Raises:
        UserError: Si ffmpeg o ffprobe no están en el `PATH`.
    """
    for binary in ("ffmpeg", "ffprobe"):
        if shutil.which(binary) is None:
            raise UserError(
                msg=_("%(binary)s was not found in PATH. Install ffmpeg first.")
                % {"binary": binary}
            )
