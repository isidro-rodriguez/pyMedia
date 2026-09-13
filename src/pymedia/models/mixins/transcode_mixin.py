"""Mixin de transcodificación."""

from dataclasses import dataclass

from pymedia.data.audio_codecs import AUDIO_CODECS
from pymedia.data.video_codecs import VIDEO_CODECS
from pymedia.errors import MissingParameterError
from pymedia.models.config import Transcode
from pymedia.models.media import Media


@dataclass(kw_only=True)
class TranscodeMixin:
    """Mixin para los parámetros de transcodificación.

    Attributes:
        transcode: Perfil de transcodificación presente en config.toml.
        transcode_video: Permite la transcodificación de la pista de video.
    """

    media: Media | None = None
    stream_tracks: list[int] | None = None
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
