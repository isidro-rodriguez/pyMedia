"""Mixin de transcodificación."""

from dataclasses import dataclass
from pathlib import Path

from pymedia.data.audio_codecs import AUDIO_CODECS
from pymedia.data.video_codecs import VIDEO_CODECS
from pymedia.errors import MissingParameterError
from pymedia.models.config import Transcode
from pymedia.models.media import Media
from pymedia.utils import to_ffmpeg_value

# Códecs de subtítulos de texto convertibles a `mov_text` (MP4).
_TEXT_SUBTITLES = frozenset({"subrip", "srt", "ass", "ssa", "mov_text", "webvtt"})


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

    def to_subtitles_copy_cmd(self, container: str) -> list[str]:
        """Construye los argumentos para conservar las pistas de subtítulos.

        Args:
            container: Extensión del contenedor de salida (p. ej. `.mp4`).

        Returns:
            Argumentos `-map` y `-c:s` por pista. En MP4 los subtítulos de texto
            se convierten a `mov_text` y los gráficos se descartan, ya que el
            contenedor no los soporta.
        """
        if self.media is None:
            raise MissingParameterError(name="media")
        if self.media.subtitles is None:
            raise MissingParameterError(name="subtitles")

        is_mp4 = container.lower() in {".mp4", ".m4v", ".mov"}
        args: list[str] = []
        output_index = 0
        for track in self.media.subtitles:
            if is_mp4 and track.codec not in _TEXT_SUBTITLES:
                continue
            codec = "mov_text" if is_mp4 and track.codec != "mov_text" else "copy"
            args.extend(
                ["-map", f"0:s:{track.track_index}", f"-c:s:{output_index}", codec]
            )
            output_index += 1
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
