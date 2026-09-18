"""Comando ``edit-subs``: cli."""

import typer

from pymedia.commands.edit_subs.parameters import EditSubtitlesParameters
from pymedia.commands.edit_subs.service import EditSubtitlesService
from pymedia.locales import _  # noqa
from pymedia.logger import Logger
from pymedia.typer.options import (
    DebugOption,
    HelpOption,
    MediaInputArgument,
    OutputOption,
    OverwriteOption,
    SubtitlesDefaultOption,
    SubtitlesForcedOption,
    SubtitlesHearingImpairedOption,
    SubtitlesLanguageOption,
    SubtitlesStreamTrackOption,
    SubtitlesTitleOption,
    SubtitlesVisualImpairedOption,
)
from pymedia.types import OverwriteMode

edit_subs_cli = typer.Typer()

EDIT_SUBS_HELP = _(
    """\
Edit subtitles metadata from a media file.

[bold]Examples[/bold]:
  Edit language metadata to subtitles stream track 2 from a media container:
    > pymedia edit-subs input.mp4 --track 2 --language eng
  Edit multiple tags in a single call: 
    > pymedia edit-subs input.mp4 --track 2 --language spa --title "Español (forced)" --default --forced
"""  # noqa
)


@edit_subs_cli.command(
    name="edit-subs",
    help=EDIT_SUBS_HELP,
    rich_help_panel="Subtitles commands",
    no_args_is_help=True,
)
def edit_subs(
    media_input: MediaInputArgument,
    subtitles_stream_tracks: SubtitlesStreamTrackOption,
    language: SubtitlesLanguageOption = None,
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
    """Punto de entrada del comando que edita metadatos de subtítulos.

    Args:
        media_input: Ruta del fichero de vídeo a procesar.
        subtitles_stream_tracks: Índice de la pista de subtítulos a editar.
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
        MissingParameterError: Si falta la pista a editar, el medio, las pistas
            de subtítulos del medio o la salida procesada.
        UserError: Si el idioma no sigue el estándar ISO 639-2 o la pista
            indicada no existe en el contenedor.
    """
    # Logger.create configura el logger raíz (nivel DEBUG) de forma idempotente;
    # params y service lo recuperan después con Logger.load().
    Logger.create(debug=debug)
    params = EditSubtitlesParameters.load(
        overwrite=overwrite,
        media_input=media_input,
        subtitles_stream_tracks=subtitles_stream_tracks,
        language=language,
        media_output=media_output,
        title=title,
        forced=forced,
        default=default,
        hearing_impaired=hearing_impaired,
        visual_impaired=visual_impaired,
    )
    EditSubtitlesService(debug=debug, params=params).start()
