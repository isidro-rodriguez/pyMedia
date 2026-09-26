"""Comando ``add-audio``: cli."""

import typer

from pymedia.commands.add_audio.parameters import AddAudioParameters
from pymedia.commands.add_audio.service import AddAudioService
from pymedia.commands.base_cli_options import (
    AudioArgument,
    DebugOption,
    HelpOption,
    MediaInputArgument,
    OutputOption,
    OverwriteOption,
    ShowCmdOption,
    StripMetadataOption,
)
from pymedia.locales import translate as _
from pymedia.logger import Logger
from pymedia.types import OverwriteMode

add_audio_cli = typer.Typer()

ADD_AUDIO_HELP = _(
    """\
Add an audio track to a media file.

You can consult what audio tracks have a container with `info` command.

The audio track's metadata (language, title, dispositions) are inherited from
the source audio file. Use `edit-audio` to modify them after insertion.

[bold]Examples[/bold]:
  Add audio track from a file (metadata inherited from source):
    > pymedia add-audio input.mp4 audio.m4a
  Add audio and override default disposition:
    > pymedia add-audio input.mp4 audio.m4a
    Then: pymedia edit-audio output.mp4 --track 1 --default
"""  # noqa
)


@add_audio_cli.command(
    name="add-audio",
    help=ADD_AUDIO_HELP,
    rich_help_panel=_("Audio commands"),
    no_args_is_help=True,
)
def add_audio(
    media_input: MediaInputArgument,
    audio_input: AudioArgument,
    media_output: OutputOption = None,
    overwrite: OverwriteOption = OverwriteMode.ASK,
    strip_metadata: StripMetadataOption = False,
    debug: DebugOption = False,
    show_cmd: ShowCmdOption = False,
    help_: HelpOption = False,
) -> None:
    """Punto de entrada del comando ``add-audio``.

    Args:
        media_input: Ruta del fichero de vídeo a procesar.
        audio_input: Ruta del fichero de audio a insertar.
        media_output: Ruta absoluta del fichero de salida procesado.
        overwrite: Política ante conflicto de salida ya existente.
        strip_metadata: No copiar los metadatos del fichero de entrada.
        debug: Habilita el nivel de log DEBUG.
        show_cmd: Muestra al usuario el comando ffmpeg compuesto pero no lo ejecuta.
        help_: Helper para mostrar esta línea en distintos idiomas.

    Raises:
        FfprobeError: Si ffprobe no puede leer el fichero de audio externo.
        MissingParameterError: Si falta el medio o el fichero de audio.
        InvalidCodecContainerError: Si el códec del audio no es
            compatible con el contenedor de salida.
    """
    Logger.create(debug=debug)
    params = AddAudioParameters.load(
        overwrite=overwrite,
        media_input=media_input,
        audio_input=audio_input,
        media_output=media_output,
        strip_metadata=strip_metadata,
    )
    AddAudioService(debug=debug, show_cmd=show_cmd, params=params).start()
