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
    SubtitlesArgument,
    SubtitlesDefaultOption,
    SubtitlesForcedOption,
    SubtitlesHearingImpairedOption,
    SubtitlesLanguageOption,
    SubtitlesTitleOption,
    SubtitlesVisualImpairedOption,
)
from pymedia.locales import _  # noqa
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
    media_output: OutputOption = None,
    overwrite: OverwriteOption = OverwriteMode.ASK,
    title: SubtitlesTitleOption = None,
    forced: SubtitlesForcedOption = False,
    default: SubtitlesDefaultOption = False,
    hearing_impaired: SubtitlesHearingImpairedOption = False,
    visual_impaired: SubtitlesVisualImpairedOption = False,
    debug: DebugOption = False,
    help_: HelpOption = False,  # noqa
) -> None:
    """Punto de entrada del comando ``add-subs``.

    Args:
        media_input: Ruta del fichero de vídeo a procesar.
        subtitles_input: Ruta del fichero de subtítulos a insertar.
        language: Código de idioma de la pista de subtítulos.
        media_output: Ruta absoluta del fichero de salida procesado.
        overwrite: Política ante conflicto de salida ya existente.
        title: Título a mostrar para identificar la pista de subtítulos.
        forced: Fuerza al reproductor a mostrar la pista de subtítulos.
        default: Se establece como la pista de subtítulos por defecto.
        hearing_impaired: Subtítulos adaptados a personas con problemas auditivos.
        visual_impaired: Subtítulos adaptados a personas con problemas de vista.
        debug: Habilita el nivel de log DEBUG.
        help_: Helper para mostrar esta línea en distintos idiomas.

    Raises:
        FfprobeError: Si ffprobe no puede leer el fichero de subtítulos.
        MissingArgumentError: Si no se indica el idioma de la pista.
        MissingParameterError: Si falta el medio o la salida procesada.
        UserError: Si el idioma no sigue el estándar ISO 639-2 o el contenedor
            de salida no soporta ningún códec de subtítulos.
    """
    Logger.create(debug=debug)
    params = AddSubtitlesParameters.load(
        overwrite=overwrite,
        media_input=media_input,
        subtitles_input=subtitles_input,
        language=language,
        media_output=media_output,
        title=title,
        forced=forced,
        default=default,
        hearing_impaired=hearing_impaired,
        visual_impaired=visual_impaired,
    )
    AddSubtitlesService(debug=debug, params=params).start()
