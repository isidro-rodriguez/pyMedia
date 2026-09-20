"""Comando ``edit-audio``: cli."""

import typer

from pymedia.commands.base_cli_options import (
    AudioCommentaryOption,
    AudioDefaultOption,
    AudioForcedOption,
    AudioHearingImpairedOption,
    AudioLanguageOption,
    AudioStreamTrackOption,
    AudioTitleOption,
    DebugOption,
    HelpOption,
    MediaInputArgument,
    OutputOption,
    OverwriteOption,
)
from pymedia.commands.edit_audio.parameters import EditAudioParameters
from pymedia.commands.edit_audio.service import EditAudioService
from pymedia.errors import MissingRequiredOptionsError
from pymedia.locales import _  # noqa
from pymedia.logger import Logger
from pymedia.types import OverwriteMode

edit_audio_cli = typer.Typer()

EDIT_AUDIO_HELP = _(
    """\
Edit audio track metadata from a media file.

You can consult what audio tracks have a container with `info` command.

[bold]Examples[/bold]:
  Edit language metadata of audio stream track 1 from a media container:
    > pymedia edit-audio input.mp4 --track 1 --language eng
  Edit multiple tags in a single call: 
    > pymedia edit-audio input.mp4 --track 1 --language spa --title "Comentario director" --default --commentary
"""  # noqa
)


@edit_audio_cli.command(
    name="edit-audio",
    help=EDIT_AUDIO_HELP,
    rich_help_panel=_("Audio commands"),
    no_args_is_help=True,
)
def edit_audio(
    media_input: MediaInputArgument,
    audio_stream_tracks: AudioStreamTrackOption,
    language: AudioLanguageOption = None,
    media_output: OutputOption = None,
    overwrite: OverwriteOption = OverwriteMode.ASK,
    title: AudioTitleOption = None,
    forced: AudioForcedOption = None,
    default: AudioDefaultOption = None,
    hearing_impaired: AudioHearingImpairedOption = None,
    commentary: AudioCommentaryOption = None,
    debug: DebugOption = False,
    help_: HelpOption = False,  # noqa
) -> None:
    """Punto de entrada del comando ``edit-audio``.

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

    Raises:
        MissingParameterError: Si falta la pista a editar, el medio, las
            pistas de audio del medio o la salida procesada.
        UserError: Si el idioma no sigue el estándar ISO 639-2 o la pista
            indicada no existe en el contenedor.
    """
    if (
        language is None
        and title is None
        and forced is None
        and default is None
        and hearing_impaired is None
        and commentary is None
    ):
        raise MissingRequiredOptionsError(
            options=[
                "language",
                "title",
                "forced",
                "default",
                "hearing_impaired",
                "commentary",
            ]
        )

    Logger.create(debug=debug)
    params = EditAudioParameters.load(
        overwrite=overwrite,
        media_input=media_input,
        audio_stream_tracks=audio_stream_tracks,
        language=language,
        media_output=media_output,
        title=title,
        forced=forced,
        default=default,
        hearing_impaired=hearing_impaired,
        commentary=commentary,
    )
    EditAudioService(debug=debug, params=params).start()
