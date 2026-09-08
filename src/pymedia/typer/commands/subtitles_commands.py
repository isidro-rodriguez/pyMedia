"""Comandos de la familia de subtítulos."""

import typer

from pymedia.locales import _  # noqa
from pymedia.pipeline.subtitles_pipeline import SubtitlesPipeline
from pymedia.typer.options import (
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
    SubtitlesStreamTrackListOption,
    SubtitlesStreamTrackOption,
    SubtitlesTitleOption,
    SubtitlesVisualImpairedOption,
)
from pymedia.types import OverwriteMode, SubtitlesMode

subtitles_typer = typer.Typer()

# =============================================================================
#  Subcomando ADD
# =============================================================================

_HELP_ADD = _(
    """\
Add subtitles to a media file.

[bold]Examples[/bold]:
  Add english subtitles to a media container:
    > pymedia add-subs input.mp4 eng_subs.srt --language eng
  Add default forced spanish subtitles with custom title: 
    > pymedia add-subs input.mp4 eng_subs.srt --language spa --title "Español (forced)" --default --forced
"""  # noqa
)


@subtitles_typer.command(
    name="add-subs",
    help=_HELP_ADD,
    rich_help_panel="Subtitles commands",
    no_args_is_help=True,
)
def add(
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
    """Punto de entrada de Typer: construye los argumentos y ejecuta el comando.

    Args:
        media_input: Ruta del fichero de vídeo a procesar.
        subtitles_input: Ruta del fichero de subtítulos a añadir.
        language: Código de idioma de la pista de subtítulos.
        media_output: Ruta absoluta del fichero de salida procesado.
        overwrite: Política ante conflicto de salida ya existente.
        title: Título a mostrar para identificar la pista de subtítulos.
        forced: Fuerza al reproductor a mostrar la pista de subtítulos.
        default: Se establece como la pista de subtítulos por defecto del contenedor.
        hearing_impaired: Subtítulos adaptados a personas con problemas auditivos.
        visual_impaired: Subtítulos adaptados a personas con problemas de vista.
        debug: Habilita el nivel de log DEBUG.
        help_: Helper para mostrar esta línea en distintos idiomas.
    """
    pipeline = SubtitlesPipeline(debug=debug)
    pipeline.process_parameters(
        media_input=media_input,
        media_output=media_output,
        overwrite=overwrite,
        subtitles_mode=SubtitlesMode.ADD,
        subtitles_input=subtitles_input,
        subtitles_language=language,
        subtitles_title=title,
        subtitles_forced=forced,
        subtitles_default=default,
        subtitles_hearing_impaired=hearing_impaired,
        subtitles_visual_impaired=visual_impaired,
    )
    if not pipeline.resolve_overwrite():
        return
    pipeline.process_cmd()


# =============================================================================
#  Subcomando DELETE
# =============================================================================

_HELP_DELETE = _(
    """\
Delete subtitles from a media file.

[bold]Examples[/bold]:
  Delete all subtitles from a media file:
    > pymedia delete-subs input.mp4
  Delete a list of subtitles tracks from a media file: 
    > pymedia delete-subs input.mp4 --tracks 3,4,5
"""  # noqa
)


@subtitles_typer.command(
    name="delete-subs",
    help=_HELP_DELETE,
    rich_help_panel="Subtitles commands",
    no_args_is_help=True,
)
def delete(
    media_input: MediaInputArgument,
    subtitles_stream_tracks: SubtitlesStreamTrackListOption = None,
    media_output: OutputOption = None,
    overwrite: OverwriteOption = OverwriteMode.ASK,
    debug: DebugOption = False,
    help_: HelpOption = False,  # noqa
) -> None:
    """Punto de entrada de Typer: construye los argumentos y ejecuta el comando.

    Args:
        media_input: Ruta del fichero de vídeo a procesar.
        subtitles_stream_tracks: Lista de pistas de subtítulos a eliminar.
        media_output: Ruta absoluta del fichero de salida procesado.
        overwrite: Política ante conflicto de salida ya existente.
        debug: Habilita el nivel de log DEBUG.
        help_: Helper para mostrar esta línea en distintos idiomas.
    """
    pipeline = SubtitlesPipeline(debug=debug)
    pipeline.process_parameters(
        media_input=media_input,
        subtitles_stream_tracks=subtitles_stream_tracks,
        media_output=media_output,
        overwrite=overwrite,
        subtitles_mode=SubtitlesMode.DELETE,
    )
    if not pipeline.resolve_overwrite():
        return
    pipeline.process_cmd()


# =============================================================================
#  Subcomando EDIT
# =============================================================================

_HELP_EDIT = _(
    """\
Edit subtitles metadata from a media file.

[bold]Examples[/bold]:
  Edit language metadata to subtitles stream track 2 from a media container:
    > pymedia edit-subs input.mp4 --track 2 --language eng
  Edit multiple tags in a single call: 
    > pymedia edit-subs input.mp4 --track 2 --language spa --title "Español (forced)" --default --forced
"""  # noqa
)


@subtitles_typer.command(
    name="edit-subs",
    help=_HELP_EDIT,
    rich_help_panel="Subtitles commands",
    no_args_is_help=True,
)
def edit(
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
    """Punto de entrada de Typer: construye los argumentos y ejecuta el comando.

    Args:
        media_input: Ruta del fichero de vídeo a procesar.
        subtitles_stream_tracks: Índice de la pista de subtítulos a editar.
        language: Código de idioma de la pista de subtítulos.
        media_output: Ruta absoluta del fichero de salida procesado.
        overwrite: Política ante conflicto de salida ya existente.
        title: Título a mostrar para identificar la pista de subtítulos.
        forced: Fuerza al reproductor a mostrar la pista de subtítulos.
        default: Se establece como la pista de subtítulos por defecto del contenedor.
        hearing_impaired: Subtítulos adaptados a personas con problemas auditivos.
        visual_impaired: Subtítulos adaptados a personas con problemas de vista.
        debug: Habilita el nivel de log DEBUG.
        help_: Helper para mostrar esta línea en distintos idiomas.
    """
    pipeline = SubtitlesPipeline(debug=debug)
    pipeline.process_parameters(
        media_input=media_input,
        subtitles_stream_tracks=subtitles_stream_tracks,
        media_output=media_output,
        overwrite=overwrite,
        subtitles_mode=SubtitlesMode.EDIT,
        subtitles_language=language,
        subtitles_title=title,
        subtitles_forced=forced,
        subtitles_default=default,
        subtitles_hearing_impaired=hearing_impaired,
        subtitles_visual_impaired=visual_impaired,
    )
    if not pipeline.resolve_overwrite():
        return
    pipeline.process_cmd()


# =============================================================================
#  Subcomando EXTRACT
# =============================================================================

_HELP_EXTRACT = _(
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


@subtitles_typer.command(
    name="extract-subs",
    help=_HELP_EXTRACT,
    rich_help_panel="Subtitles commands",
    no_args_is_help=True,
)
def extract(
    media_input: MediaInputArgument,
    subtitles_stream_tracks: SubtitlesStreamTrackListOption = None,
    subtitles_output: OutputOption = None,
    overwrite: OverwriteOption = OverwriteMode.ASK,
    debug: DebugOption = False,
    help_: HelpOption = False,  # noqa
) -> None:
    """Punto de entrada de Typer: construye los argumentos y ejecuta el comando.

    Args:
        media_input: Ruta del fichero de vídeo a procesar.
        subtitles_stream_tracks: Lista de pistas de subtítulos a eliminar.
        subtitles_output: Ruta absoluta del fichero de subtítulos de salida.
        overwrite: Política ante conflicto de salida ya existente.
        debug: Habilita el nivel de log DEBUG.
        help_: Helper para mostrar esta línea en distintos idiomas.
    """
    pipeline = SubtitlesPipeline(debug=debug)
    pipeline.process_parameters(
        media_input=media_input,
        subtitles_stream_tracks=subtitles_stream_tracks,
        subtitles_output=subtitles_output,
        overwrite=overwrite,
        subtitles_mode=SubtitlesMode.EXTRACT,
    )
    if not pipeline.resolve_overwrite():
        return
    pipeline.process_cmd()
