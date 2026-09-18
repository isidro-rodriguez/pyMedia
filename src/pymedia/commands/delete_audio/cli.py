"""Comando ``delete-audio``: cli."""

import typer

from pymedia.commands.delete_audio.parameters import DeleteAudioParameters
from pymedia.commands.delete_audio.service import DeleteAudioService
from pymedia.locales import _  # noqa
from pymedia.logger import Logger
from pymedia.typer.options import (
    AudioStreamTrackListOption,
    DebugOption,
    HelpOption,
    MediaInputArgument,
    OutputOption,
    OverwriteOption,
)
from pymedia.types import OverwriteMode

delete_audio_cli = typer.Typer()

DELETE_AUDIO_HELP = _(
    """\
Delete audio tracks from a media file.

[bold]Examples[/bold]:
  Delete all audio tracks from a media file:
    > pymedia delete-audio input.mp4
  Delete a list of audio tracks from a media file: 
    > pymedia delete-audio input.mp4 --tracks 1,2
"""  # noqa
)


@delete_audio_cli.command(
    name="delete-audio",
    help=DELETE_AUDIO_HELP,
    rich_help_panel="Audio commands",
    no_args_is_help=True,
)
def delete_audio(
    media_input: MediaInputArgument,
    audio_stream_tracks: AudioStreamTrackListOption = None,
    media_output: OutputOption = None,
    overwrite: OverwriteOption = OverwriteMode.ASK,
    debug: DebugOption = False,
    help_: HelpOption = False,  # noqa
) -> None:
    """Punto de entrada del comando que elimina pistas de audio.

    Args:
        media_input: Ruta del fichero de vídeo a procesar.
        audio_stream_tracks: Lista de pistas de audio a eliminar.
        media_output: Ruta absoluta del fichero de salida procesado.
        overwrite: Política ante conflicto de salida ya existente.
        debug: Habilita el nivel de log DEBUG.
        help_: Helper para mostrar esta línea en distintos idiomas.

    Raises:
        MissingParameterError: Si falta el medio, las pistas de audio del
            medio o la salida procesada.
        UserError: Si el formato del listado o algún índice no es válido.
    """
    # Logger.create configura el logger raíz (nivel DEBUG) de forma idempotente;
    # params y service lo recuperan después con Logger.load().
    Logger.create(debug=debug)
    params = DeleteAudioParameters.load(
        overwrite=overwrite,
        media_input=media_input,
        audio_stream_tracks=audio_stream_tracks,
        media_output=media_output,
    )
    DeleteAudioService(debug=debug, params=params).start()
