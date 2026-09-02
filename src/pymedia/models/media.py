"""Modelos de metadatos de medios obtenidos mediante ffprobe."""

from dataclasses import dataclass
from datetime import timedelta
from fractions import Fraction
from pathlib import Path

from pymedia.ffmpeg.probe import probe
from pymedia.logger import Logger
from pymedia.utils import parse_fraction, to_float, to_int


@dataclass(frozen=True, kw_only=True, slots=True)
class Video:
    """Metadatos de la pista de vídeo de un medio.

    Attributes:
        codec: Nombre del códec de vídeo.
        width: Ancho en píxeles.
        height: Alto en píxeles.
        fps: Frecuencia de imágenes por segundo.
        bit_rate: Tasa de bits en bps.
        pix_fmt: Formato de píxeles.
        aspect_ratio: Relación de aspecto mostrada.
        profile: Perfil del códec.
    """

    codec: str | None = None
    width: int | None = None
    height: int | None = None
    fps: Fraction | None = None
    bit_rate: int | None = None
    pix_fmt: str | None = None
    aspect_ratio: str | None = None
    profile: str | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class Audio:
    """Metadatos de una pista de audio de un medio.

    Attributes:
        codec: Nombre del códec de audio.
        sample_rate: Frecuencia de muestreo en Hz.
        channels: Número de canales.
        channel_layout: Distribución de canales (p. ej. "stereo").
        bit_rate: Tasa de bits en bps.
        language: Código de idioma de la pista.
    """

    codec: str | None = None
    sample_rate: int | None = None
    channels: int | None = None
    channel_layout: str | None = None
    bit_rate: int | None = None
    language: str | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class Subtitle:
    """Metadatos de una pista de subtítulos de un medio.

    Attributes:
        index: Índice de la pista dentro del contenedor.
        codec: Nombre del códec de subtítulos.
        language: Código de idioma de la pista.
        title: Título descriptivo de la pista.
        forced: Si la pista está marcada como forzada.
        default: Si la pista está marcada como predeterminada.
    """

    index: int | None = None
    codec: str | None = None
    language: str | None = None
    title: str | None = None
    forced: bool | None = None
    default: bool | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class Media:
    """Metadatos agregados de un medio obtenidos de ffprobe.

    Attributes:
        duration: Duración total del medio.
        size: Tamaño del fichero en bytes.
        format_name: Nombre del formato contenedor.
        video: Metadatos de la pista de vídeo, o None si no existe.
        audio: Lista de pistas de audio, o None si no hay.
        subtitles: Lista de pistas de subtítulos, o None si no hay.
    """

    duration: timedelta | None = None
    size: int | None = None
    format_name: str | None = None
    video: Video | None = None
    audio: list[Audio] | None = None
    subtitles: list[Subtitle] | None = None

    @classmethod
    def load(cls, path: Path, logger: Logger) -> "Media":
        """Mapea el JSON de ffprobe a MediaInput.

        Args:
            path: Ruta del fichero multimedia a analizar.
            logger: Logger para los mensajes del proceso ffprobe.

        Returns:
            El medio construido a partir de la salida de ffprobe.
        """
        data = probe(path=path, logger=logger)

        video = None
        audio = None
        subtitles = None

        for stream in data.get("streams", []):
            codec_type = stream.get("codec_type")
            tags = stream.get("tags", {})
            language = tags.get("language")

            if codec_type == "video":
                video = Video(
                    codec=stream.get("codec_name"),
                    width=stream.get("width"),
                    height=stream.get("height"),
                    fps=parse_fraction(stream.get("avg_frame_rate")),
                    bit_rate=to_int(stream.get("bit_rate")),
                    pix_fmt=stream.get("pix_fmt"),
                    aspect_ratio=stream.get("display_aspect_ratio"),
                    profile=stream.get("profile"),
                )
            elif codec_type == "audio":
                if audio is None:
                    audio = []
                audio.append(
                    Audio(
                        codec=stream.get("codec_name"),
                        sample_rate=to_int(stream.get("sample_rate")),
                        channels=stream.get("channels"),
                        channel_layout=stream.get("channel_layout"),
                        bit_rate=to_int(stream.get("bit_rate")),
                        language=language,
                    )
                )
            elif codec_type == "subtitle":
                if subtitles is None:
                    subtitles = []
                disposition = stream.get("disposition", {})
                subtitles.append(
                    Subtitle(
                        index=stream.get("index"),
                        codec=stream.get("codec_name"),
                        language=language,
                        title=tags.get("title"),
                        forced=bool(disposition.get("forced")),
                        default=bool(disposition.get("default")),
                    )
                )

        fmt = data.get("format", {})
        duration_val = to_float(fmt.get("duration"))

        return Media(
            duration=timedelta(seconds=duration_val)
            if duration_val is not None
            else None,
            size=to_int(fmt.get("size")),
            format_name=fmt.get("format_name"),
            video=video,
            audio=audio,
            subtitles=subtitles,
        )
