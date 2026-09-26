"""Ejecución de ffprobe para obtener los metadatos de un medio."""

import json
import subprocess
from datetime import timedelta
from pathlib import Path
from typing import Any

from pymedia.data.subtitles_formats import SUBTITLES_FORMATS
from pymedia.data.video_codecs import VIDEO_CODECS
from pymedia.errors import FfprobeError, MissingParameterError, UserError
from pymedia.locales import translate as _
from pymedia.logger import Logger
from pymedia.models.audio import Audio, AudioMetadata
from pymedia.models.media import Media, MediaMetadata
from pymedia.models.subtitles import Subtitles, SubtitlesMetadata
from pymedia.models.video import Video
from pymedia.utils import parse_date, parse_fraction, to_float, to_int


def _run_ffprobe(args: list[str], path: Path) -> dict[str, Any]:
    """Ejecuta ffprobe y devuelve su JSON, con un error breve si falla."""
    cmd = ["ffprobe", "-v", "error", "-print_format", "json", *args, str(path)]
    try:
        result = subprocess.run(
            args=cmd,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError as err:
        raise FfprobeError(msg=_("ffprobe was not found. Install ffmpeg.")) from err
    except subprocess.CalledProcessError as err:
        lines = [line for line in err.stderr.splitlines() if line.strip()]
        reason = lines[-1] if lines else str(err.returncode)
        raise FfprobeError(
            msg=_("ffprobe couldn't read %(path)s: %(err.stderr)s")
            % {"path": path, "err.stderr": reason}
        ) from err

    data: dict[str, Any] = json.loads(result.stdout)

    return data


def _build_audio_metadata(
    tags: dict[str, Any], disposition: dict[str, Any]
) -> AudioMetadata:
    """Construye AudioMetadata a partir de tags y disposition de ffprobe."""
    language = tags.get("language")
    return AudioMetadata(
        language=language,
        title=tags.get("title"),
        forced=bool(disposition.get("forced", 0)),
        default=bool(disposition.get("default", 0)),
        hearing_impaired=bool(disposition.get("hearing_impaired", 0)),
        commentary=bool(disposition.get("comment", 0)),
        dubbed=bool(disposition.get("dub", 0)),
        original=bool(disposition.get("original", 0)),
        lyrics=bool(disposition.get("lyrics", 0)),
        karaoke=bool(disposition.get("karaoke", 0)),
        visual_impaired=bool(disposition.get("visual_impaired", 0)),
        clean_effects=bool(disposition.get("clean_effects", 0)),
    )


def get_media_information(media_input: Path, logger: Logger) -> "Media":
    """Obtiene información del contenedor multimedia.

    Raises:
        UserError: Si el contenedor no tiene pista de vídeo.
        FfprobeError: Si ffprobe no puede leer el archivo.
        MissingParameterError: Si faltan parámetros requeridos.
    """
    data = _run_ffprobe(["-show_format", "-show_streams"], media_input)
    logger.debug(msg=_("ffprobe media data: %(data)s"), data=data)

    video: Video | None = None
    audio: list[Audio] | None = None
    subtitles: list[Subtitles] | None = None
    video_track_index, audio_track_index, subtitles_track_index = 0, 0, 0

    for stream in data.get("streams", []):
        codec_type = stream.get("codec_type")
        tags = stream.get("tags", {})
        disposition = stream.get("disposition", {})

        if codec_type == "video":
            video = Video(
                path=media_input.absolute(),
                global_index=stream.get("index"),
                track_index=video_track_index,
                codec=VIDEO_CODECS[stream.get("codec_name")].name,
                width=stream.get("width"),
                height=stream.get("height"),
                duration=tags.get("DURATION"),
                fps=parse_fraction(stream.get("avg_frame_rate")),
                bit_rate=to_int(stream.get("bit_rate")),
                pix_fmt=stream.get("pix_fmt"),
                aspect_ratio=stream.get("display_aspect_ratio"),
                profile=stream.get("profile"),
            )
            video_track_index += 1
        elif codec_type == "audio":
            if audio is None:
                audio = []
            audio.append(
                Audio(
                    path=media_input.absolute(),
                    global_index=stream.get("index"),
                    track_index=audio_track_index,
                    codec=stream.get("codec_name"),
                    duration=tags.get("DURATION"),
                    sample_rate=to_int(stream.get("sample_rate")),
                    channels=stream.get("channels"),
                    channel_layout=stream.get("channel_layout"),
                    bit_rate=to_int(stream.get("bit_rate")),
                    metadata=_build_audio_metadata(tags, disposition),
                )
            )
            audio_track_index += 1
        elif codec_type == "subtitle":
            # ffprobe reporta el valor en singular para las pistas de subtítulos.
            if subtitles is None:
                subtitles = []
            disposition = stream.get("disposition", {})
            subtitles.append(
                Subtitles(
                    path=media_input.absolute(),
                    global_index=stream.get("index"),
                    track_index=subtitles_track_index,
                    codec=stream.get("codec_name"),
                    metadata=SubtitlesMetadata(
                        language=tags.get("language"),
                        title=tags.get("title"),
                        forced=bool(disposition.get("forced", 0)),
                        default=bool(disposition.get("default", 0)),
                        hearing_impaired=bool(disposition.get("hearing_impaired", 0)),
                        visual_impaired=bool(disposition.get("visual_impaired", 0)),
                    ),
                )
            )
            subtitles_track_index += 1

    if video is None:
        raise UserError(
            msg=_("Invalid video container: %(path)s") % {"path": str(media_input)}
        )

    fmt = data.get("format", {})
    tags = fmt.get("tags", {})
    duration_val = to_float(fmt.get("duration"))

    try:
        media_metadata = MediaMetadata(
            title=tags.get("title"),
            comment=tags.get("COMMENT"),
            description=tags.get("DESCRIPTION"),
            synopsis=tags.get("SYNOPSIS"),
            genre=tags.get("GENRE"),
            date=parse_date(raw=tags.get("DATE")),
            copyright=tags.get("COPYRIGHT"),
            law_rating=tags.get("LAW_RATING"),
            artist=tags.get("ARTIST"),
            album=tags.get("ALBUM"),
            encoder=tags.get("ENCODER"),
        )

        media = Media(
            path=media_input.absolute(),
            duration=timedelta(seconds=duration_val)
            if duration_val is not None
            else None,
            size=to_int(fmt.get("size")),
            format_name=fmt.get("format_name"),
            video=video,
            audio=audio,
            subtitles=subtitles,
            metadata=media_metadata if tags else None,
        )
    except (
        ValueError,
        subprocess.CalledProcessError,
        json.JSONDecodeError,
        OSError,
    ) as e:
        raise MissingParameterError(name="media") from e

    return media


def get_audio_information(audio_input: Path, logger: Logger) -> list[Audio]:
    """Obtiene información del fichero de audio.

    Args:
        audio_input: Ruta del archivo de audio a verificar.
        logger: Servicio de registro de mensajes.

    Raises:
        FfprobeError: Si ffprobe no puede leer el archivo, no detecta un
            formato de audio conocido, o el formato detectado no es
            compatible con la extensión del archivo.
        UserError: Si el archivo no contiene pistas de audio.

    Returns:
        Lista de pistas de audio con sus metadatos.
    """
    data = _run_ffprobe(
        args=["-show_format", "-show_streams"],
        path=audio_input,
    )
    logger.debug(msg=_("ffprobe audio file data: %(data)s"), data=data)

    audio: list[Audio] = []
    audio_track_index, video_tracks, subtitles_tracks = 0, 0, 0

    for stream in data.get("streams", []):
        codec_type = stream.get("codec_type")
        tags = stream.get("tags", {})
        disposition = stream.get("disposition", {})

        if codec_type == "audio":
            audio.append(
                Audio(
                    path=audio_input.absolute(),
                    global_index=stream.get("index"),
                    track_index=audio_track_index,
                    codec=stream.get("codec_name"),
                    duration=tags.get("DURATION"),
                    sample_rate=to_int(stream.get("sample_rate")),
                    channels=stream.get("channels"),
                    channel_layout=stream.get("channel_layout"),
                    bit_rate=to_int(stream.get("bit_rate")),
                    metadata=_build_audio_metadata(tags, disposition),
                )
            )
            audio_track_index += 1
        elif codec_type == "video":
            video_tracks += 1
        elif codec_type == "subtitle":
            subtitles_tracks += 1

    if len(audio) == 0:
        raise UserError(
            msg=_("It doesn't contain any audio track. Invalid audio file: %(file)s")
            % {"file": audio_input}
        )

    if video_tracks > 0:
        logger.warning(
            msg=_("Audio file contains video tracks: %(tracks)s")
            % {"tracks": video_tracks}
        )
    if subtitles_tracks > 0:
        logger.warning(
            msg=_("Audio file contains subtitles tracks: %(tracks)s")
            % {"tracks": subtitles_tracks}
        )

    return audio


def validate_subtitles_file_codec(subtitles_input: Path, logger: Logger) -> None:
    """Verifica que el archivo de subtítulos externo sea realmente subtítulos.

    Args:
        subtitles_input: Ruta del archivo de subtítulos a verificar.
        logger: Servicio de registro de mensajes.

    Raises:
        FfprobeError: Si ffprobe no puede leer el archivo, no detecta un
            formato de subtítulos conocido, o el formato detectado no es
            compatible con la extensión del archivo.
    """
    data = _run_ffprobe(["-show_format"], subtitles_input)
    logger.debug(msg=_("ffprobe subtitles file data: %(data)s"), data=data)

    format_name = data.get("format", {}).get("format_name", "")
    detected_codecs: set[str] = {
        token.strip() for token in format_name.split(",") if token.strip()
    }
    codec_name = next(
        (c for c in detected_codecs if c in SUBTITLES_FORMATS),
        None,
    )
    if codec_name is None:
        raise FfprobeError(
            msg=_(
                '"%(path)s" is not a recognized subtitles file '
                "(detected format: %(format_name)s)."
            )
            % {"path": subtitles_input, "format_name": format_name or "unknown"}
        )

    fmt = SUBTITLES_FORMATS.get(codec_name)
    if fmt is None or subtitles_input.suffix.lower() not in fmt.containers:
        raise FfprobeError(
            msg=_("%(path.suffix)s extension doesn't support %(codec_name)s subtitles.")
            % {"path.suffix": subtitles_input.suffix, "codec_name": codec_name}
        )
