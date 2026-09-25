"""Comando ``extract-subs``: cli."""

import typer

from pymedia.commands.base_cli_options import (
    DebugOption,
    HelpOption,
    MediaInputArgument,
    OutputOption,
    OverwriteOption,
    ShowCmdOption,
    StripMetadataOption,
    SubtitlesStreamTrackListOption,
)
from pymedia.commands.extract_subtitles.parameters import ExtractSubtitlesParameters
from pymedia.commands.extract_subtitles.service import ExtractSubtitlesService
from pymedia.locales import _
from pymedia.logger import Logger
from pymedia.types import OverwriteMode

extract_subs_cli = typer.Typer()

EXTRACT_SUBS_HELP = _(
    """\
Extract subtitles from a media file.

You can consult what subtitles tracks have a container with `info` command.

[bold]Examples[/bold]:
  Extract a list of subtitles tracks from a media file:
    > pymedia extract-subs input.mp4 --tracks 3,4,5
  Extract subtitles tracks with custom output:
    > pymedia extract-subs input.mp4 --tracks 3,5 -o input-subtitles.srt
"""
)


@extract_subs_cli.command(
    name="extract-subs",
    help=EXTRACT_SUBS_HELP,
    rich_help_panel=_("Subtitles commands"),
    no_args_is_help=True,
)
def extract_subs(
    media_input: MediaInputArgument,
    subtitles_stream_tracks: SubtitlesStreamTrackListOption,
    subtitles_output: OutputOption = None,
    overwrite: OverwriteOption = OverwriteMode.ASK,
    strip_metadata: StripMetadataOption = False,
    debug: DebugOption = False,
    show_cmd: ShowCmdOption = False,
    help_: HelpOption = False,
) -> None:
    """Punto de entrada del comando ``extract-subs``.

    Args:
        media_input: Ruta del fichero de vídeo a procesar.
        subtitles_stream_tracks: Lista de pistas de subtítulos a extraer.
        subtitles_output: Ruta absoluta del fichero de subtítulos de salida.
        overwrite: Política ante conflicto de salida ya existente.
        strip_metadata: No copiar los metadatos del fichero de entrada.
        debug: Habilita el nivel de log DEBUG.
        show_cmd: Muestra al usuario el comando ffmpeg compuesto pero no lo ejecuta.
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
    Logger.create(debug=debug)
    params = ExtractSubtitlesParameters.load(
        overwrite=overwrite,
        media_input=media_input,
        subtitles_stream_tracks=subtitles_stream_tracks,
        subtitles_output=subtitles_output,
        strip_metadata=strip_metadata,
    )
    ExtractSubtitlesService(debug=debug, show_cmd=show_cmd, params=params).start()
