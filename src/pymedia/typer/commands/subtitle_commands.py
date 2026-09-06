"""Comandos de la familia de subtítulos."""

import typer

from pymedia.locales import _  # noqa
from pymedia.pipeline.subtitles_add_pipeline import SubtitlesAddPipeline
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
    SubtitlesTitleOption,
    SubtitlesVisualImpairedOption,
)
from pymedia.types import OverwriteMode

subtitles_typer = typer.Typer()

# =============================================================================
#  Subcomando FRAMES
# =============================================================================

_HELP_FRAMES = _(
    """\
Add subtitles to a media file.

[bold]Examples[/bold]:
  Add english subtitles to a media container:
    > pymedia add input.mp4 eng_subs.srt --language eng
  Add default forced spanish subtitles with custom title: 
    > pymedia add input.mp4 eng_subs.srt --language spa --title "Español (forced)" --default --forced
"""  # noqa
)


@subtitles_typer.command(
    name="add",
    help=_HELP_FRAMES,
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
    pipeline = SubtitlesAddPipeline(debug=debug)
    pipeline.process_parameters(
        media_input=media_input,
        media_output=media_output,
        overwrite=overwrite,
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
