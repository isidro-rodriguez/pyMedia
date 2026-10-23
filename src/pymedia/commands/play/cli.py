"""Comando ``play``: cli."""

import typer

from pymedia.commands.base.cli_options import (
    CropOption,
    DebugOption,
    FlipHorizontalOption,
    FlipVerticalOption,
    HelpOption,
    MediaInputArgument,
    PlayAudioOption,
    PlayBurnSubtitlesOption,
    PlayEndOption,
    PlayFullscreenOption,
    PlayLoopOption,
    PlayMuteOption,
    PlayNoSubtitlesOption,
    PlayStartOption,
    PlaySubtitlesOption,
    PlayVolumeOption,
    RotateOption,
    ScaleModeOption,
    ScaleToOption,
    ScaleUpscaleOption,
    ShowCmdOption,
)
from pymedia.commands.play.parameters import PlayParameters
from pymedia.commands.play.service import PlayService
from pymedia.locales import translate as _
from pymedia.logger import Logger
from pymedia.types import ScaleMode
from pymedia.ui import styled_help

play_cli = typer.Typer()

PLAY_HELP = _(
    """\
Plays a video with ffplay.

Useful to preview a cut, an audio or subtitles track, or image filters
before processing the file.

[bold]Examples[/bold]:
  Play a video:
    > pymedia play input.mkv
  Play a range with the second audio track and the first subtitles track:
    > pymedia play input.mkv --start 10:00 --end 12:30 --audio 1 --subs 0
  Preview image filters before transcoding:
    > pymedia play input.mp4 --crop 1280,720,0,0 --hflip

[bold]Keys[/bold]:
  space pause · ←/→ seek 10 s · ↓/↑ seek 1 min · 9/0 volume · m mute
  a audio track · t subtitles track · f full screen · q quit
"""
)


@play_cli.command(
    name="play",
    help=styled_help(PLAY_HELP),
    rich_help_panel=_("Analysis commands"),
    no_args_is_help=True,
)
def play(
    media_input: MediaInputArgument,
    timestamp_start: PlayStartOption = None,
    timestamp_end: PlayEndOption = None,
    audio_track: PlayAudioOption = None,
    subtitles_track: PlaySubtitlesOption = None,
    no_subtitles: PlayNoSubtitlesOption = False,
    subtitles_input: PlayBurnSubtitlesOption = None,
    mute: PlayMuteOption = False,
    volume: PlayVolumeOption = None,
    loop: PlayLoopOption = False,
    fullscreen: PlayFullscreenOption = False,
    crop: CropOption = None,
    rotate: RotateOption = None,
    scale_to: ScaleToOption = None,
    scale_mode: ScaleModeOption = ScaleMode.FIT,
    scale_upscale: ScaleUpscaleOption = False,
    hflip: FlipHorizontalOption = False,
    vflip: FlipVerticalOption = False,
    debug: DebugOption = False,
    show_cmd: ShowCmdOption = False,
    _help: HelpOption = False,
) -> None:
    """Punto de entrada del comando ``play``.

    Args:
        media_input: Ruta del fichero de vídeo a reproducir.
        timestamp_start: Marca de tiempo donde empieza la reproducción.
        timestamp_end: Marca de tiempo donde termina la reproducción.
        audio_track: Índice de la pista de audio a reproducir.
        subtitles_track: Índice de la pista de subtítulos a mostrar.
        no_subtitles: Oculta los subtítulos del contenedor.
        subtitles_input: Fichero de subtítulos externo a dibujar.
        mute: Reproduce sin audio.
        volume: Volumen inicial en porcentaje (0-100).
        loop: Repite la reproducción indefinidamente.
        fullscreen: Abre la ventana a pantalla completa.
        crop: Área y coordenada de la zona a preservar de la imagen.
        rotate: Ángulo ortogonal con el que se va a rotar la imagen.
        scale_to: Dimensión objetivo en píxeles.
        scale_mode: Política de escalado del vídeo o imagen.
        scale_upscale: Permite el incremento de dimensiones.
        hflip: Invierte la imagen horizontalmente.
        vflip: Invierte la imagen verticalmente.
        debug: Habilita el nivel de log DEBUG.
        show_cmd: Muestra al usuario el comando ffplay compuesto, pero no lo ejecuta.
        _help: Helper para mostrar esta línea en distintos idiomas.
    """
    Logger.create(debug=debug)
    params = PlayParameters.load(
        media_input=media_input,
        timestamp_start=timestamp_start,
        timestamp_end=timestamp_end,
        audio_track=audio_track,
        subtitles_track=subtitles_track,
        subtitles_input=subtitles_input,
        no_subtitles=no_subtitles,
        mute=mute,
        volume=volume,
        loop=loop,
        fullscreen=fullscreen,
        crop=crop,
        scale_to=scale_to,
        scale_mode=scale_mode,
        scale_upscale=scale_upscale,
        rotate=rotate,
        hflip=hflip,
        vflip=vflip,
    )
    PlayService(debug=debug, show_cmd=show_cmd, params=params).start()
