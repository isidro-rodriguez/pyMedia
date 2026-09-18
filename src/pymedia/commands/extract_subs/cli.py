"""Comando ``extract-subs``: cli."""

import typer

from pymedia.commands.extract_subs.parameters import ExtractSubtitlesParameters
from pymedia.commands.extract_subs.service import ExtractSubtitlesService
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

extract_subs_cli = typer.Typer()

EXTRACT_SUBS_HELP = _(
    """\
Extract subtitles from a media file.

[bold]Examples[/bold]:
  Extract all subtitles from a media file:
    > pymedia extract-subs input.mp4
  Extract a list of subtitles tracks from a media file: 
    > pymedia extract-subs input.mp4 --tracks 3,4,5
  Extract subtitles tracks with custom output:
    > pymedia extract-subs input.mp4 --tracks 3,5 -o input-subtitles.srt
"""  # noqa
)


@extract_subs_cli.command(
    name="extract-subs",
    help=EXTRACT_SUBS_HELP,
    rich_help_panel="Subtitles commands",
    no_args_is_help=True,
)
def extract_subs(
    media_input: MediaInputArgument,
    subtitles_stream_tracks: SubtitlesStreamTrackListOption = None,
    subtitles_output: OutputOption = None,
    overwrite: OverwriteOption = OverwriteMode.ASK,
    debug: DebugOption = False,
    help_: HelpOption = False,  # noqa
) -> None:
    """Punto de entrada del comando que extrae pistas de subtítulos.

    Args:
        media_input: Ruta del fichero de vídeo a procesar.
        subtitles_stream_tracks: Lista de pistas de subtítulos a extraer.
        subtitles_output: Ruta absoluta del fichero de subtítulos de salida.
        overwrite: Política ante conflicto de salida ya existente.
        debug: Habilita el nivel de log DEBUG.
        help_: Helper para mostrar esta línea en distintos idiomas.

    Raises:
        InvalidContainerError: Si la extensión de salida no es un fichero de
            subtítulos soportado.
        MissingParameterError: Si falta el medio, las pistas de subtítulos del
            medio o la salida procesada.
        MissingPropertyError: Si el medio no declara las pistas de subtítulos o
            el códec de alguna de ellas.
        UserError: Si el medio no tiene pistas de subtítulos, el formato del
            listado, algún índice o el nombre de salida no son válidos.
    """
    # Logger.create configura el logger raíz (nivel DEBUG) de forma idempotente;
    # params y service lo recuperan después con Logger.load().
    Logger.create(debug=debug)
    params = ExtractSubtitlesParameters.load(
        overwrite=overwrite,
        media_input=media_input,
        subtitles_stream_tracks=subtitles_stream_tracks,
        subtitles_output=subtitles_output,
    )
    ExtractSubtitlesService(debug=debug, params=params).start()
