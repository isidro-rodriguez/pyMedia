"""Comando ``extract-audio``: cli."""

import typer

from pymedia.commands.base_cli_options import (
    AudioStreamTrackListOption,
    DebugOption,
    HelpOption,
    MediaInputArgument,
    OutputOption,
    OverwriteOption,
)
from pymedia.commands.extract_audio.parameters import ExtractAudioParameters
from pymedia.commands.extract_audio.service import ExtractAudioService
from pymedia.locales import _  # noqa
from pymedia.logger import Logger
from pymedia.types import OverwriteMode

extract_audio_cli = typer.Typer()

EXTRACT_AUDIO_HELP = _(
    """\
Extract audio tracks from a media file.

You can consult what audio tracks have a container with `info` command.

[bold]Examples[/bold]:
  Extract a list of audio tracks from a media file: 
    > pymedia extract-audio input.mp4 --tracks 1,2
  Extract audio tracks with custom output:
    > pymedia extract-audio input.mp4 --tracks 1,2 -o input-audio.m4a
"""  # noqa
)


@extract_audio_cli.command(
    name="extract-audio",
    help=EXTRACT_AUDIO_HELP,
    rich_help_panel=_("Audio commands"),
    no_args_is_help=True,
)
def extract_audio(
    media_input: MediaInputArgument,
    audio_stream_tracks: AudioStreamTrackListOption,
    audio_output: OutputOption = None,
    overwrite: OverwriteOption = OverwriteMode.ASK,
    debug: DebugOption = False,
    help_: HelpOption = False,  # noqa
) -> None:
    """Punto de entrada del comando ``extract-audio``.

    Args:
        media_input: Ruta del fichero de vídeo a procesar.
        audio_stream_tracks: Lista de pistas de audio a extraer.
        audio_output: Ruta absoluta del fichero de audio de salida.
        overwrite: Política ante conflicto de salida ya existente.
        debug: Habilita el nivel de log DEBUG.
        help_: Helper para mostrar esta línea en distintos idiomas.

    Raises:
        InvalidContainerError: Si la extensión de salida no es una pista de
            audio soportada.
        MissingParameterError: Si falta el medio, las pistas de audio del medio
            o la salida procesada.
        MissingPropertyError: Si el medio no declara las pistas de audio o el
            códec de alguna de ellas.
        UserError: Si el formato del listado, algún índice o el nombre de
            salida no son válidos.
    """
    Logger.create(debug=debug)
    params = ExtractAudioParameters.load(
        overwrite=overwrite,
        media_input=media_input,
        audio_stream_tracks=audio_stream_tracks,
        audio_output=audio_output,
    )
    ExtractAudioService(debug=debug, params=params).start()
