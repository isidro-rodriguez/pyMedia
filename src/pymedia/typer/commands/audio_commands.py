"""Comandos de la familia de audio."""

import typer

from pymedia.pipeline.audio_pipeline import AudioPipeline
from pymedia.typer.help import (
    AUDIO_ADD_HELP,
    AUDIO_DELETE_HELP,
    AUDIO_EDIT_HELP,
    AUDIO_EXTRACT_HELP,
)
from pymedia.typer.options import (
    AudioArgument,
    AudioCommentaryOption,
    AudioDefaultOption,
    AudioForcedOption,
    AudioHearingImpairedOption,
    AudioLanguageOption,
    AudioStreamTrackListOption,
    AudioStreamTrackOption,
    AudioTitleOption,
    DebugOption,
    HelpOption,
    MediaInputArgument,
    OutputOption,
    OverwriteOption,
)
from pymedia.types import AudioMode, OverwriteMode

audio_typer = typer.Typer()

# =============================================================================
#  Subcomando ADD
# =============================================================================


@audio_typer.command(
    name="add-audio",
    help=AUDIO_ADD_HELP,
    rich_help_panel="Audio commands",
    no_args_is_help=True,
)
def add(
    media_input: MediaInputArgument,
    audio_input: AudioArgument,
    language: AudioLanguageOption,
    media_output: OutputOption = None,
    overwrite: OverwriteOption = OverwriteMode.ASK,
    title: AudioTitleOption = None,
    forced: AudioForcedOption = False,
    default: AudioDefaultOption = False,
    hearing_impaired: AudioHearingImpairedOption = False,
    commentary: AudioCommentaryOption = False,
    debug: DebugOption = False,
    help_: HelpOption = False,  # noqa
) -> None:
    """Punto de entrada de Typer: construye los argumentos y ejecuta el comando.

    Args:
        media_input: Ruta del fichero de vídeo a procesar.
        audio_input: Ruta del fichero de audio a añadir.
        language: Código de idioma de la pista de audio.
        media_output: Ruta absoluta del fichero de salida procesado.
        overwrite: Política ante conflicto de salida ya existente.
        title: Título a mostrar para identificar la pista de audio.
        forced: Fuerza al reproductor a usar la pista de audio.
        default: Se establece como la pista de audio por defecto del contenedor.
        hearing_impaired: Pista orientada a personas con problemas auditivos.
        commentary: Pista de comentarios de audio.
        debug: Habilita el nivel de log DEBUG.
        help_: Helper para mostrar esta línea en distintos idiomas.
    """
    pipeline = AudioPipeline(debug=debug)
    pipeline.process_parameters(
        media_input=media_input,
        media_output=media_output,
        overwrite=overwrite,
        audio_mode=AudioMode.ADD,
        audio_input=audio_input,
        audio_language=language,
        audio_title=title,
        audio_forced=forced,
        audio_default=default,
        audio_hearing_impaired=hearing_impaired,
        audio_commentary=commentary,
    )
    if not pipeline.resolve_overwrite():
        return
    pipeline.process_cmd()


# =============================================================================
#  Subcomando DELETE
# =============================================================================


@audio_typer.command(
    name="delete-audio",
    help=AUDIO_DELETE_HELP,
    rich_help_panel="Audio commands",
    no_args_is_help=True,
)
def delete(
    media_input: MediaInputArgument,
    audio_stream_tracks: AudioStreamTrackListOption = None,
    media_output: OutputOption = None,
    overwrite: OverwriteOption = OverwriteMode.ASK,
    debug: DebugOption = False,
    help_: HelpOption = False,  # noqa
) -> None:
    """Punto de entrada de Typer: construye los argumentos y ejecuta el comando.

    Args:
        media_input: Ruta del fichero de vídeo a procesar.
        audio_stream_tracks: Lista de pistas de audio a eliminar.
        media_output: Ruta absoluta del fichero de salida procesado.
        overwrite: Política ante conflicto de salida ya existente.
        debug: Habilita el nivel de log DEBUG.
        help_: Helper para mostrar esta línea en distintos idiomas.
    """
    pipeline = AudioPipeline(debug=debug)
    pipeline.process_parameters(
        media_input=media_input,
        audio_stream_tracks=audio_stream_tracks,
        media_output=media_output,
        overwrite=overwrite,
        audio_mode=AudioMode.DELETE,
    )
    if not pipeline.resolve_overwrite():
        return
    pipeline.process_cmd()


# =============================================================================
#  Subcomando EDIT
# =============================================================================


@audio_typer.command(
    name="edit-audio",
    help=AUDIO_EDIT_HELP,
    rich_help_panel="Audio commands",
    no_args_is_help=True,
)
def edit(
    media_input: MediaInputArgument,
    audio_stream_tracks: AudioStreamTrackOption,
    language: AudioLanguageOption = None,
    media_output: OutputOption = None,
    overwrite: OverwriteOption = OverwriteMode.ASK,
    title: AudioTitleOption = None,
    forced: AudioForcedOption = False,
    default: AudioDefaultOption = False,
    hearing_impaired: AudioHearingImpairedOption = False,
    commentary: AudioCommentaryOption = False,
    debug: DebugOption = False,
    help_: HelpOption = False,  # noqa
) -> None:
    """Punto de entrada de Typer: construye los argumentos y ejecuta el comando.

    Args:
        media_input: Ruta del fichero de vídeo a procesar.
        audio_stream_tracks: Índice de la pista de audio a editar.
        language: Código de idioma de la pista de audio.
        media_output: Ruta absoluta del fichero de salida procesado.
        overwrite: Política ante conflicto de salida ya existente.
        title: Título a mostrar para identificar la pista de audio.
        forced: Fuerza al reproductor a usar la pista de audio.
        default: Se establece como la pista de audio por defecto del contenedor.
        hearing_impaired: Pista orientada a personas con problemas auditivos.
        commentary: Pista de comentarios de audio.
        debug: Habilita el nivel de log DEBUG.
        help_: Helper para mostrar esta línea en distintos idiomas.
    """
    pipeline = AudioPipeline(debug=debug)
    pipeline.process_parameters(
        media_input=media_input,
        audio_stream_tracks=audio_stream_tracks,
        media_output=media_output,
        overwrite=overwrite,
        audio_mode=AudioMode.EDIT,
        audio_language=language,
        audio_title=title,
        audio_forced=forced,
        audio_default=default,
        audio_hearing_impaired=hearing_impaired,
        audio_commentary=commentary,
    )
    if not pipeline.resolve_overwrite():
        return
    pipeline.process_cmd()


# =============================================================================
#  Subcomando EXTRACT
# =============================================================================


@audio_typer.command(
    name="extract-audio",
    help=AUDIO_EXTRACT_HELP,
    rich_help_panel="Audio commands",
    no_args_is_help=True,
)
def extract(
    media_input: MediaInputArgument,
    audio_stream_tracks: AudioStreamTrackListOption = None,
    audio_output: OutputOption = None,
    overwrite: OverwriteOption = OverwriteMode.ASK,
    debug: DebugOption = False,
    help_: HelpOption = False,  # noqa
) -> None:
    """Punto de entrada de Typer: construye los argumentos y ejecuta el comando.

    Args:
        media_input: Ruta del fichero de vídeo a procesar.
        audio_stream_tracks: Lista de pistas de audio a extraer.
        audio_output: Ruta absoluta del fichero de audio de salida.
        overwrite: Política ante conflicto de salida ya existente.
        debug: Habilita el nivel de log DEBUG.
        help_: Helper para mostrar esta línea en distintos idiomas.
    """
    pipeline = AudioPipeline(debug=debug)
    pipeline.process_parameters(
        media_input=media_input,
        audio_stream_tracks=audio_stream_tracks,
        audio_output=audio_output,
        overwrite=overwrite,
        audio_mode=AudioMode.EXTRACT,
    )
    if not pipeline.resolve_overwrite():
        return
    pipeline.process_cmd()
