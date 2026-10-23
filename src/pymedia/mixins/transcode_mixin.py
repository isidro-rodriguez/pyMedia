"""Mixin de transcodificación."""

from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

from pymedia.data.audio_codecs import AUDIO_CODECS
from pymedia.data.subtitles_formats import SUBTITLES_FORMATS
from pymedia.data.video_codecs import VIDEO_CODECS
from pymedia.errors import MissingParameterError
from pymedia.models.config import Transcode
from pymedia.models.media import Media
from pymedia.models.subtitles import Subtitles
from pymedia.utils import to_ffmpeg_value

# Códecs de subtítulos de texto, convertibles entre sí.
_TEXT_SUBTITLES = frozenset({"subrip", "srt", "ass", "ssa", "mov_text", "webvtt"})
# Nombre de ffprobe → clave de `SUBTITLES_FORMATS`.
_SUBTITLES_ALIASES = MappingProxyType({"subrip": "srt", "ssa": "ass"})
# Códec de texto al que se convierten los subtítulos según el contenedor de salida.
_TEXT_SUBTITLES_TARGET = MappingProxyType(
    {".mkv": "srt", ".mov": "mov_text", ".mp4": "mov_text", ".webm": "webvtt"}
)


@dataclass(kw_only=True)
class TranscodeMixin:
    """Mixin para los parámetros de transcodificación.

    Attributes:
        transcode: Perfil de transcodificación presente en config.toml.
        transcode_video: Permite la transcodificación de la pista de video.
    """

    media: Media | None = None
    stream_tracks: list[int] | None = None
    subtitles_input: Path | None = None
    transcode: Transcode
    transcode_video: bool
    convert_subtitles: bool = True

    def to_video_transcode_cmd(self) -> list[str]:
        """Construye la secuencia de argumentos para la transcodificación de vídeo.

        Returns:
            Argumentos `-c:v copy` si la transcodificación de vídeo está
            desactivada, o los del perfil de transcodificación configurado.
        """
        if not self.transcode_video:
            return ["-c:v", "copy"]

        video_transcode: list[str] = [
            "-c:v",
            VIDEO_CODECS[self.transcode.video_codec].library,
            "-crf",
            str(self.transcode.video_crf),
            "-preset",
            self.transcode.video_preset,
        ]

        pix_fmt = VIDEO_CODECS[self.transcode.video_codec].pix_fmt
        if pix_fmt is not None:
            video_transcode.extend(["-pix_fmt", pix_fmt])

        return video_transcode

    def to_audio_transcode_cmd(self) -> list[str]:
        """Construye la secuencia de argumentos para la transcodificación de audio.

        Returns:
            Argumentos `-map` y `-c:a` para cada pista de audio, con `copy`
            para las pistas fuera del listado a transcodificar.

        Raises:
            MissingParameterError: Si el medio no tiene pistas de audio.
        """
        media = self.media
        if media is None:
            raise MissingParameterError(name="media")
        if media.audio is None:
            raise MissingParameterError(name="media.audio")

        tracks_to_transcode: list[int] = (
            self.stream_tracks if self.stream_tracks else []
        )

        audio_transcode: list[str] = []
        for audio_track in media.audio:
            audio_transcode.extend(
                [
                    "-map",
                    f"0:a:{audio_track.track_index}",
                    f"-c:a:{audio_track.track_index}",
                ]
            )
            if audio_track.track_index in tracks_to_transcode:
                codec_data = AUDIO_CODECS[self.transcode.audio_codec]
                audio_transcode.append(codec_data.library)
                # Los códecs sin pérdida no aceptan el flag -b:a.
                if codec_data.bit_rates is not None:
                    audio_transcode.extend(
                        [
                            f"-b:a:{audio_track.track_index}",
                            self.transcode.audio_bit_rate,
                        ]
                    )
            else:
                audio_transcode.append("copy")
        return audio_transcode

    def incompatible_subtitles(self, container: str) -> list[Subtitles]:
        """Devuelve las pistas de subtítulos que el contenedor no admite sin convertir.

        Args:
            container: Extensión del contenedor de salida (p. ej. `.mp4`).

        Returns:
            Pistas cuyo códec no se puede copiar al contenedor de salida.
        """
        if self.media is None or not self.media.subtitles:
            return []
        return [
            track
            for track in self.media.subtitles
            if not _fits_container(track=track, container=container.lower())
        ]

    def to_subtitles_copy_cmd(self, container: str) -> list[str]:
        """Construye los argumentos para conservar las pistas de subtítulos.

        Las pistas compatibles con el contenedor se copian. Las de texto
        incompatibles se convierten al códec de texto del contenedor si
        `convert_subtitles` es `True`; el resto se descartan.

        Args:
            container: Extensión del contenedor de salida (p. ej. `.mp4`).

        Returns:
            Argumentos `-map` y `-c:s` por pista conservada.

        Raises:
            MissingParameterError: Si falta el medio o sus subtítulos.
        """
        if self.media is None:
            raise MissingParameterError(name="media")
        if self.media.subtitles is None:
            raise MissingParameterError(name="subtitles")

        container = container.lower()
        target = _TEXT_SUBTITLES_TARGET.get(container)
        args: list[str] = []
        for track in self.media.subtitles:
            if _fits_container(track=track, container=container):
                codec = "copy"
            elif self.convert_subtitles and target and is_text_subtitles(track):
                codec = target
            else:
                continue
            output_index = len(args) // 4
            args.extend(
                ["-map", f"0:s:{track.track_index}", f"-c:s:{output_index}", codec]
            )
        return args

    def to_burn_subtitles_cmd(self) -> str:
        """Construye el filtro que quema los subtítulos en la pista de vídeo.

        Returns:
            Filtro `subtitles` con la ruta escapada para el parser de filtergraph,
            sin comillas: el comando no pasa por un shell y ffmpeg no admite
            comillas simples anidadas.

        Raises:
            MissingParameterError: Si no se indicó el fichero de subtítulos.
        """
        if self.subtitles_input is None:
            raise MissingParameterError(name="subtitles")

        return f"subtitles={to_ffmpeg_value(self.subtitles_input.absolute())}"


def is_text_subtitles(track: Subtitles) -> bool:
    """Indica si la pista de subtítulos es de texto (convertible a otro formato).

    Args:
        track: Pista de subtítulos a comprobar.

    Returns:
        `True` si la pista es de texto, `False` si es gráfica o desconocida.
    """
    if track.format.is_text_based is not None:
        return track.format.is_text_based
    return track.format.codec in _TEXT_SUBTITLES


def _fits_container(track: Subtitles, container: str) -> bool:
    """Indica si el códec de la pista se puede copiar al contenedor."""
    codec = track.format.codec or ""
    fmt = SUBTITLES_FORMATS.get(_SUBTITLES_ALIASES.get(codec, codec))
    # Un códec fuera del catálogo se copia tal cual y ffmpeg decide.
    return fmt is None or container in fmt.containers
