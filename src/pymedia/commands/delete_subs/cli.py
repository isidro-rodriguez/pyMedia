"""Comando ``delete-subs``: cli."""

import typer

from pymedia.commands.delete_subs.parameters import DeleteSubtitlesParameters
from pymedia.commands.delete_subs.service import DeleteSubtitlesService
from pymedia.locales import _  # noqa
from pymedia.logger import Logger
from pymedia.typer.options import (
    DebugOption,
    HelpOption,
    MediaInputArgument,
    OutputOption,
    OverwriteOption,
    SubtitlesStreamTrackListOption,
)
from pymedia.types import OverwriteMode

delete_subs_cli = typer.Typer()

DELETE_SUBS_HELP = _(
    """\
Delete subtitles from a media file.

[bold]Examples[/bold]:
  Delete all subtitles from a media file:
    > pymedia delete-subs input.mp4
  Delete a list of subtitles tracks from a media file: 
    > pymedia delete-subs input.mp4 --tracks 3,4,5
"""  # noqa
)


@delete_subs_cli.command(
    name="delete-subs",
    help=DELETE_SUBS_HELP,
    rich_help_panel="Subtitles commands",
    no_args_is_help=True,
)
def delete_subs(
    media_input: MediaInputArgument,
    subtitles_stream_tracks: SubtitlesStreamTrackListOption = None,
    media_output: OutputOption = None,
    overwrite: OverwriteOption = OverwriteMode.ASK,
    debug: DebugOption = False,
    help_: HelpOption = False,  # noqa
) -> None:
    """Punto de entrada del comando que elimina pistas de subtítulos.

    Args:
        media_input: Ruta del fichero de vídeo a procesar.
        subtitles_stream_tracks: Lista de pistas de subtítulos a eliminar.
        media_output: Ruta absoluta del fichero de salida procesado.
        overwrite: Política ante conflicto de salida ya existente.
        debug: Habilita el nivel de log DEBUG.
        help_: Helper para mostrar esta línea en distintos idiomas.

    Raises:
        MissingParameterError: Si falta el medio, las pistas de subtítulos del
            medio o la salida procesada.
        UserError: Si el medio no tiene pistas de subtítulos, el formato del
            listado o algún índice no es válido.
    """
    # Logger.create configura el logger raíz (nivel DEBUG) de forma idempotente;
    # params y service lo recuperan después con Logger.load().
    Logger.create(debug=debug)
    params = DeleteSubtitlesParameters.load(
        overwrite=overwrite,
        media_input=media_input,
        subtitles_stream_tracks=subtitles_stream_tracks,
        media_output=media_output,
    )
    DeleteSubtitlesService(debug=debug, params=params).start()
