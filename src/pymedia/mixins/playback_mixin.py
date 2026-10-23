"""Mixin con las opciones de reproducción de ffplay."""

from dataclasses import dataclass
from pathlib import Path

from pymedia.errors import MissingParameterError, UserError
from pymedia.ffprobe import validate_subtitles_file_codec
from pymedia.locales import translate as _
from pymedia.logger import Logger
from pymedia.mixins.streams_mixin import StreamsMixin
from pymedia.types import StreamsMode
from pymedia.utils import to_ffmpeg_value

MAX_VOLUME = 100
"""Volumen máximo de ffplay (`-volume`), en porcentaje."""


@dataclass(kw_only=True)
class PlaybackMixin(StreamsMixin):
    """Mixin con las pistas, el sonido y la ventana de la reproducción.

    Attributes:
        audio_track: Índice de la pista de audio a reproducir.
        subtitles_track: Índice de la pista de subtítulos a mostrar.
        subtitles_input: Fichero de subtítulos externo a dibujar sobre el vídeo.
        no_subtitles: Oculta los subtítulos del contenedor.
        mute: Reproduce sin audio.
        volume: Volumen inicial en porcentaje (0-100).
        loop: Repite la reproducción indefinidamente.
        fullscreen: Abre la ventana a pantalla completa.
    """

    audio_track: int | None = None
    subtitles_track: int | None = None
    subtitles_input: Path | None = None
    no_subtitles: bool = False
    mute: bool = False
    volume: int | None = None
    loop: bool = False
    fullscreen: bool = False

    def create_playback(
        self,
        logger: Logger,
        *,
        audio_track: int | None = None,
        subtitles_track: int | None = None,
        subtitles_input: Path | None = None,
        no_subtitles: bool = False,
        mute: bool = False,
        volume: int | None = None,
        loop: bool = False,
        fullscreen: bool = False,
    ) -> None:
        """Valida las opciones de reproducción y crea sus atributos.

        Args:
            logger: Sistema de registro de mensajes.
            audio_track: Índice de la pista de audio a reproducir.
            subtitles_track: Índice de la pista de subtítulos a mostrar.
            subtitles_input: Fichero de subtítulos externo a dibujar.
            no_subtitles: Oculta los subtítulos del contenedor.
            mute: Reproduce sin audio.
            volume: Volumen inicial en porcentaje (0-100).
            loop: Repite la reproducción indefinidamente.
            fullscreen: Abre la ventana a pantalla completa.

        Raises:
            UserError: Si se combinan opciones excluyentes, el volumen está
                fuera de rango o una pista no existe en el contenedor.
            FfprobeError: Si el fichero de subtítulos externo no es válido.
            MissingParameterError: Si no se obtuvo el medio de entrada.
        """
        if mute and audio_track is not None:
            raise _exclusive_error("--mute", "--audio")

        subtitles_options = {
            "--subs": subtitles_track is not None,
            "--no-subs": no_subtitles,
            "--burn-subtitles": subtitles_input is not None,
        }
        used = [option for option, given in subtitles_options.items() if given]
        if len(used) > 1:
            raise _exclusive_error(*used)

        if volume is not None and not 0 <= volume <= MAX_VOLUME:
            raise UserError(
                msg=_("Volume must be between 0 and %(max)s.") % {"max": MAX_VOLUME}
            )

        if audio_track is not None:
            self._validate_track(track=audio_track, streams_type=StreamsMode.AUDIO)
        if subtitles_track is not None:
            self._validate_track(
                track=subtitles_track, streams_type=StreamsMode.SUBTITLES
            )
        if subtitles_input is not None:
            validate_subtitles_file_codec(
                subtitles_input=subtitles_input, logger=logger
            )

        self.audio_track = audio_track
        self.subtitles_track = subtitles_track
        self.subtitles_input = subtitles_input
        self.no_subtitles = no_subtitles
        self.mute = mute
        self.volume = volume
        self.loop = loop
        self.fullscreen = fullscreen

    def to_playback_cmd(self) -> list[str]:
        """Devuelve las opciones de ffplay para pistas, sonido y ventana.

        Returns:
            Lista de argumentos de ffplay; vacía si no hay ninguna opción.
        """
        cmd: list[str] = []

        if self.mute:
            cmd.append("-an")
        elif self.audio_track is not None:
            cmd.extend(["-ast", f"a:{self.audio_track}"])

        # Al dibujar un fichero externo se ocultan los subtítulos del contenedor.
        if self.no_subtitles or self.subtitles_input is not None:
            cmd.append("-sn")
        elif self.subtitles_track is not None:
            cmd.extend(["-sst", f"s:{self.subtitles_track}"])

        if self.volume is not None:
            cmd.extend(["-volume", str(self.volume)])
        if self.loop:
            cmd.extend(["-loop", "0"])
        if self.fullscreen:
            cmd.append("-fs")

        return cmd

    def to_subtitles_overlay_cmd(self) -> str:
        """Construye el filtro que dibuja el fichero de subtítulos externo.

        Returns:
            Filtro `subtitles` con la ruta escapada para el parser de filtergraph.

        Raises:
            MissingParameterError: Si no se indicó el fichero de subtítulos.
        """
        if self.subtitles_input is None:
            raise MissingParameterError(name="subtitles_input")
        return f"subtitles={to_ffmpeg_value(self.subtitles_input.absolute())}"

    def _validate_track(self, track: int, streams_type: StreamsMode) -> None:
        """Valida que la pista exista, también si el medio no tiene de ese tipo."""
        if self.media is None:
            raise MissingParameterError(name="media")
        if streams_type == StreamsMode.AUDIO and self.media.audio is None:
            raise UserError(msg=_("Audio index not included."))
        if streams_type == StreamsMode.SUBTITLES and self.media.subtitles is None:
            raise UserError(msg=_("Subtitles index not included."))
        self._validate_stream(track=track, streams_type=streams_type)


def _exclusive_error(*options: str) -> UserError:
    """Error de opciones que no se pueden combinar."""
    return UserError(
        msg=_("These options cannot be combined: %(options)s")
        % {"options": ", ".join(options)}
    )
