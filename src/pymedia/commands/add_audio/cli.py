"""Comando ``add-audio``: cli."""

import typer

from pymedia.commands.add_audio.parameters import AddAudioParameters
from pymedia.commands.add_audio.service import AddAudioService
from pymedia.locales import _  # noqa
from pymedia.logger import Logger
from pymedia.typer.options import (
    AudioArgument,
    AudioCommentaryOption,
    AudioDefaultOption,
    AudioForcedOption,
    AudioHearingImpairedOption,
    AudioLanguageOption,
    AudioTitleOption,
    DebugOption,
    HelpOption,
    MediaInputArgument,
    OutputOption,
    OverwriteOption,
)
from pymedia.types import OverwriteMode

add_audio_cli = typer.Typer()

ADD_AUDIO_HELP = _(
    """\
Add an audio track to a media file.

[bold]Examples[/bold]:
  Add english audio to a media container:
    > pymedia add-audio input.mp4 eng_audio.aac --language eng
  Add default commentary spanish audio with custom title: 
    > pymedia add-audio input.mp4 spa_audio.aac --language spa --title "Comentario director" --default --commentary
"""  # noqa
)


@add_audio_cli.command(
    name="add-audio",
    help=ADD_AUDIO_HELP,
    rich_help_panel="Audio commands",
    no_args_is_help=True,
)
def add_audio(
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
    """Punto de entrada del comando que inserta una pista de audio.

    Args:
        media_input: Ruta del fichero de vídeo a procesar.
        audio_input: Ruta del fichero de audio a insertar.
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

    Raises:
        FfprobeError: Si ffprobe no puede leer el fichero de audio externo.
        MissingArgumentError: Si no se indica el idioma de la pista.
        MissingParameterError: Si falta el medio o el fichero de audio.
        UserError: Si el idioma no sigue el estándar ISO 639-2.
    """
    # Logger.create configura el logger raíz (nivel DEBUG) de forma idempotente;
    # params y service lo recuperan después con Logger.load().
    Logger.create(debug=debug)
    params = AddAudioParameters.load(
        overwrite=overwrite,
        media_input=media_input,
        audio_input=audio_input,
        language=language,
        media_output=media_output,
        title=title,
        forced=forced,
        default=default,
        hearing_impaired=hearing_impaired,
        commentary=commentary,
    )
    AddAudioService(debug=debug, params=params).start()
