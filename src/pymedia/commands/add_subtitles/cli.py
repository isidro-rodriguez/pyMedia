"""Comando ``add-subs``: cli."""

import typer

from pymedia.commands.add_subtitles.parameters import AddSubtitlesParameters
from pymedia.commands.add_subtitles.service import AddSubtitlesService
from pymedia.commands.base_cli_options import (
    DebugOption,
    HelpOption,
    MediaInputArgument,
    OutputOption,
    OverwriteOption,
    ShowCmdOption,
    StripMetadataOption,
    SubtitlesArgument,
    SubtitlesLanguageOption,
    SubtitlesTitleOption,
)
from pymedia.errors import MissingArgumentError
from pymedia.locales import translate as _
from pymedia.logger import Logger
from pymedia.types import OverwriteMode

add_subs_cli = typer.Typer()

ADD_SUBS_HELP = _(
    """\
Add subtitles to a media file.

You can consult what subtitles tracks have a container with `info` command.

[bold]Examples[/bold]:
  Add english subtitles to a media container:
    > pymedia add-subs input.mp4 eng_subs.srt --language eng
  Add default forced spanish subtitles with custom title:
    > pymedia add-subs input.mp4 spa_subs.srt --language spa --title "Español (forced)" --default --forced
"""  # noqa
)


@add_subs_cli.command(
    name="add-subs",
    help=ADD_SUBS_HELP,
    rich_help_panel=_("Subtitles commands"),
    no_args_is_help=True,
)
def add_subs(
    media_input: MediaInputArgument,
    subtitles_input: SubtitlesArgument,
    language: SubtitlesLanguageOption,
    title: SubtitlesTitleOption = None,
    media_output: OutputOption = None,
    overwrite: OverwriteOption = OverwriteMode.ASK,
    strip_metadata: StripMetadataOption = False,
    debug: DebugOption = False,
    show_cmd: ShowCmdOption = False,
    _help: HelpOption = False,
) -> None:
    """Punto de entrada del comando ``add-subs``.

    Args:
        media_input: Ruta del fichero de vídeo a procesar.
        subtitles_input: Ruta del fichero de subtítulos a insertar.
        language: Código de idioma de la pista de subtítulos.
        title: Título a mostrar para identificar la pista de subtítulos.
        media_output: Ruta absoluta del fichero de salida procesado.
        overwrite: Política ante conflicto de salida ya existente.
        strip_metadata: No copiar los metadatos del fichero de entrada.
        debug: Habilita el nivel de log DEBUG.
        show_cmd: Muestra al usuario el comando ffmpeg compuesto pero no lo ejecuta.
        _help: Helper para mostrar esta línea en distintos idiomas.

    Raises:
        FfprobeError: Si ffprobe no puede leer el fichero de subtítulos.
        MissingArgumentError: Si no se indica el idioma de la pista.
        MissingParameterError: Si falta el medio o la salida procesada.
        UserError: Si el idioma no sigue el estándar ISO 639-2 o el contenedor
            de salida no soporta ningún códec de subtítulos.
    """
    if language is None:
        raise MissingArgumentError(name="language")

    Logger.create(debug=debug)
    params = AddSubtitlesParameters.load(
        overwrite=overwrite,
        media_input=media_input,
        subtitles_input=subtitles_input,
        language=language,
        title=title,
        media_output=media_output,
        strip_metadata=strip_metadata,
    )
    AddSubtitlesService(debug=debug, show_cmd=show_cmd, params=params).start()
