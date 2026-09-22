"""Comando ``delete-audio``: cli."""

import typer

from pymedia.commands.base_cli_options import (
    AudioStreamTrackListOption,
    DebugOption,
    HelpOption,
    MediaInputArgument,
    OutputOption,
    OverwriteOption,
    ShowCmdOption,
)
from pymedia.commands.delete_audio.parameters import DeleteAudioParameters
from pymedia.commands.delete_audio.service import DeleteAudioService
from pymedia.locales import _
from pymedia.logger import Logger
from pymedia.types import OverwriteMode

delete_audio_cli = typer.Typer()

DELETE_AUDIO_HELP = _(
    """\
Delete audio tracks from a media file.

You can consult what audio tracks have a container with `info` command.

[bold]Examples[/bold]:
  Delete a list of audio tracks from a media file:
    > pymedia delete-audio input.mp4 --tracks 1,2
"""
)


@delete_audio_cli.command(
    name="delete-audio",
    help=DELETE_AUDIO_HELP,
    rich_help_panel=_("Audio commands"),
    no_args_is_help=True,
)
def delete_audio(
    media_input: MediaInputArgument,
    audio_stream_tracks: AudioStreamTrackListOption,
    media_output: OutputOption = None,
    overwrite: OverwriteOption = OverwriteMode.ASK,
    debug: DebugOption = False,
    show_cmd: ShowCmdOption = False,
    help_: HelpOption = False,
) -> None:
    """Punto de entrada del comando ``delete-audio``.

    Args:
        media_input: Ruta del fichero de vídeo a procesar.
        audio_stream_tracks: Lista de pistas de audio a eliminar.
        media_output: Ruta absoluta del fichero de salida procesado.
        overwrite: Política ante conflicto de salida ya existente.
        debug: Habilita el nivel de log DEBUG.
        show_cmd: Muestra al usuario el comando ffmpeg compuesto pero no lo ejecuta.
        help_: Helper para mostrar esta línea en distintos idiomas.

    Raises:
        MissingParameterError: Si falta el medio, las pistas de audio del
            medio o la salida procesada.
        UserError: Si el formato del listado o algún índice no es válido.
    """
    Logger.create(debug=debug)
    params = DeleteAudioParameters.load(
        overwrite=overwrite,
        media_input=media_input,
        audio_stream_tracks=audio_stream_tracks,
        media_output=media_output,
    )
    DeleteAudioService(debug=debug, show_cmd=show_cmd, params=params).start()
