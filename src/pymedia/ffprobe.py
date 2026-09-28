"""Ejecución de ffprobe para obtener los metadatos de un medio."""

import json
import subprocess
from datetime import timedelta
from pathlib import Path
from typing import Any

from pymedia.data.subtitles_formats import SUBTITLES_FORMATS, SubtitlesType
from pymedia.data.video_codecs import VIDEO_CODECS
from pymedia.errors import FfprobeError, MissingParameterError, UserError
from pymedia.locales import translate as _
from pymedia.logger import Logger
from pymedia.models.audio import (
    Audio,
    AudioDispositions,
    AudioFormat,
    AudioLoudness,
    AudioMetadata,
)
from pymedia.models.chapters import Chapter, ChapterFormat, ChapterMetadata
from pymedia.models.media import Media, MediaFormat, MediaMetadata
from pymedia.models.subtitles import (
    Subtitles,
    SubtitlesDispositions,
    SubtitlesFormat,
    SubtitlesMetadata,
)
from pymedia.models.video import (
    Video,
    VideoDispositions,
    VideoFormat,
    VideoMetadata,
)
from pymedia.utils import (
    parse_date,
    parse_duration,
    parse_fraction,
    parse_r128_gain,
    parse_replaygain_gain,
    ticks_to_timedelta,
    to_bool,
    to_dict,
    to_dict_list,
    to_float,
    to_int,
    to_text,
    to_timedelta,
)


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

    invalid = _("ffprobe returned invalid output for %(path)s") % {"path": path}
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as err:
        raise FfprobeError(msg=invalid) from err
    if not isinstance(data, dict):
        raise FfprobeError(msg=invalid)

    return data


def _get_tag(tags: dict[str, Any], *names: str) -> str | None:
    """Busca una etiqueta probando varias variantes de mayúsculas/minúsculas."""
    for name in names:
        for variant in (name, name.upper(), name.lower(), name.capitalize()):
            if variant in tags:
                value = tags[variant]
                return None if value is None else str(value)
    return None


def _collect_tags(tags: dict[str, Any], *known: str) -> dict[str, str]:
    """Devuelve como str las etiquetas no mapeadas explícitamente a otros campos."""
    known_lower = {name.lower() for name in known}
    return {
        key: str(value) for key, value in tags.items() if key.lower() not in known_lower
    }


def _stream_duration(stream: dict[str, Any], tags: dict[str, Any]) -> timedelta | None:
    """Duración de un stream: prioriza 'duration' sobre la etiqueta DURATION."""
    return parse_duration(stream.get("duration")) or parse_duration(
        _get_tag(tags, "duration")
    )


def _build_media_format(fmt: dict[str, Any]) -> MediaFormat:
    """Construye MediaFormat a partir del dict 'format' de ffprobe."""
    return MediaFormat(
        name=fmt.get("format_name"),
        long_name=fmt.get("format_long_name"),
        size=to_int(fmt.get("size")),
        bit_rate=to_int(fmt.get("bit_rate")),
        probe_score=to_int(fmt.get("probe_score")),
        nb_streams=to_int(fmt.get("nb_streams")),
        nb_programs=to_int(fmt.get("nb_programs")),
    )


_MEDIA_METADATA_KEYS = (
    "title",
    "comment",
    "description",
    "synopsis",
    "genre",
    "date",
    "copyright",
    "law_rating",
    "artist",
    "album",
    "encoder",
)


def _build_media_metadata(tags: dict[str, Any]) -> MediaMetadata:
    """Construye MediaMetadata a partir del dict 'tags' de ffprobe."""
    return MediaMetadata(
        title=_get_tag(tags, "title"),
        comment=_get_tag(tags, "comment"),
        description=_get_tag(tags, "description"),
        synopsis=_get_tag(tags, "synopsis"),
        genre=_get_tag(tags, "genre"),
        date=parse_date(raw=_get_tag(tags, "date")),
        copyright=_get_tag(tags, "copyright"),
        law_rating=_get_tag(tags, "law_rating"),
        artist=_get_tag(tags, "artist"),
        album=_get_tag(tags, "album"),
        encoder=_get_tag(tags, "encoder"),
        tags=_collect_tags(tags, *_MEDIA_METADATA_KEYS),
    )


def _build_audio_format(stream: dict[str, Any]) -> AudioFormat:
    """Construye AudioFormat a partir del stream de audio de ffprobe."""
    return AudioFormat(
        codec=to_text(stream.get("codec_name")),
        sample_rate=to_int(stream.get("sample_rate")),
        channels=to_int(stream.get("channels")),
        channel_layout=stream.get("channel_layout"),
        bit_rate=to_int(stream.get("bit_rate")),
    )


def _build_audio_metadata(tags: dict[str, Any]) -> AudioMetadata:
    """Construye los metadatos de audio a partir de las etiquetas del stream."""
    known = ("language", "title", "artist", "comment", "encoder")
    return AudioMetadata(
        language=_get_tag(tags, "language"),
        title=_get_tag(tags, "title"),
        artist=_get_tag(tags, "artist"),
        comment=_get_tag(tags, "comment"),
        encoder=_get_tag(tags, "encoder"),
        tags=_collect_tags(tags, *known),
    )


def _build_audio_loudness(tags: dict[str, Any]) -> AudioLoudness:
    """Construye las métricas de sonoridad a partir de etiquetas ReplayGain/R128.

    El rango dinámico (LRA) y el pico verdadero (dBTP) requieren un análisis
    con el filtro `loudnorm` de ffmpeg y no están disponibles vía ffprobe.
    """
    return AudioLoudness(
        integrated=parse_r128_gain(_get_tag(tags, "r128_track_gain")),
        replaygain_gain=parse_replaygain_gain(_get_tag(tags, "replaygain_track_gain")),
        replaygain_peak=to_float(_get_tag(tags, "replaygain_track_peak")),
    )


def _build_audio_dispositions(disposition: dict[str, Any]) -> AudioDispositions:
    """Construye AudioDispositions a partir del disposition dict de ffprobe."""
    return AudioDispositions(
        forced=to_bool(disposition.get("forced")),
        default=to_bool(disposition.get("default")),
        hearing_impaired=to_bool(disposition.get("hearing_impaired")),
        commentary=to_bool(disposition.get("comment")),
        dubbed=to_bool(disposition.get("dub")),
        original=to_bool(disposition.get("original")),
        lyrics=to_bool(disposition.get("lyrics")),
        karaoke=to_bool(disposition.get("karaoke")),
        visual_impaired=to_bool(disposition.get("visual_impaired")),
        clean_effects=to_bool(disposition.get("clean_effects")),
    )


def _build_video_format(stream: dict[str, Any]) -> VideoFormat:
    """Construye VideoFormat a partir del stream de vídeo de ffprobe."""
    codec = to_text(stream.get("codec_name"))
    known = VIDEO_CODECS.get(codec) if codec else None
    return VideoFormat(
        # Un códec ausente del catálogo no invalida el fichero: se usa el nombre crudo.
        codec=known.name if known else codec,
        width=to_int(stream.get("width")),
        height=to_int(stream.get("height")),
        fps=parse_fraction(stream.get("avg_frame_rate")),
        bit_rate=to_int(stream.get("bit_rate")),
        pix_fmt=stream.get("pix_fmt"),
        aspect_ratio=stream.get("display_aspect_ratio"),
        profile=stream.get("profile"),
        pixel_aspect_ratio=stream.get("sample_aspect_ratio"),
    )


def _build_video_metadata(tags: dict[str, Any]) -> VideoMetadata:
    """Construye VideoMetadata a partir de las etiquetas del stream de vídeo."""
    known = ("language", "title", "encoder")
    return VideoMetadata(
        language=_get_tag(tags, "language"),
        title=_get_tag(tags, "title"),
        encoder=_get_tag(tags, "encoder"),
        tags=_collect_tags(tags, *known),
    )


def _build_video_dispositions(disposition: dict[str, Any]) -> VideoDispositions:
    """Construye VideoDispositions a partir del disposition dict de ffprobe."""
    return VideoDispositions(
        default=to_bool(disposition.get("default")),
        forced=to_bool(disposition.get("forced")),
        original=to_bool(disposition.get("original")),
        commentary=to_bool(disposition.get("comment")),
        attached_pic=to_bool(disposition.get("attached_pic")),
        captions=to_bool(disposition.get("captions")),
    )


def _build_subtitles_format(stream: dict[str, Any]) -> SubtitlesFormat:
    """Construye SubtitlesFormat a partir del stream de subtítulos de ffprobe."""
    codec = to_text(stream.get("codec_name"))
    known = SUBTITLES_FORMATS.get(codec) if codec else None
    mimetype = _get_tag(to_dict(stream.get("tags")), "mimetype") or (
        known.mimetype if known else None
    )
    return SubtitlesFormat(
        codec=codec,
        mimetype=mimetype,
        is_text_based=(known.subtitles_type == SubtitlesType.TEXT) if known else None,
    )


def _build_subtitles_metadata(tags: dict[str, Any]) -> SubtitlesMetadata:
    """Construye los metadatos de subtítulos a partir de las etiquetas del stream."""
    known = ("language", "title", "encoder")
    return SubtitlesMetadata(
        language=_get_tag(tags, "language"),
        title=_get_tag(tags, "title"),
        encoder=_get_tag(tags, "encoder"),
        tags=_collect_tags(tags, *known),
    )


def _build_subtitles_dispositions(disposition: dict[str, Any]) -> SubtitlesDispositions:
    """Construye SubtitlesDispositions a partir del disposition dict de ffprobe."""
    return SubtitlesDispositions(
        default=to_bool(disposition.get("default")),
        forced=to_bool(disposition.get("forced")),
        hearing_impaired=to_bool(disposition.get("hearing_impaired")),
        visual_impaired=to_bool(disposition.get("visual_impaired")),
        original=to_bool(disposition.get("original")),
        dub=to_bool(disposition.get("dub")),
        commentary=to_bool(disposition.get("comment")),
        lyrics=to_bool(disposition.get("lyrics")),
        karaoke=to_bool(disposition.get("karaoke")),
        captions=to_bool(disposition.get("captions")),
        descriptions=to_bool(disposition.get("descriptions")),
        metadata=to_bool(disposition.get("metadata")),
    )


def _build_chapter(chapter: dict[str, Any]) -> Chapter:
    """Construye un Chapter a partir de una entrada 'chapters' de ffprobe."""
    tags = to_dict(chapter.get("tags"))
    time_base = to_text(chapter.get("time_base"))
    fraction = parse_fraction(time_base)

    return Chapter(
        id=to_int(chapter.get("id")),
        start_time=parse_duration(chapter.get("start_time")),
        end_time=parse_duration(chapter.get("end_time")),
        format=ChapterFormat(
            time_base=time_base,
            start=ticks_to_timedelta(chapter.get("start"), fraction),
            end=ticks_to_timedelta(chapter.get("end"), fraction),
        ),
        metadata=ChapterMetadata(
            title=_get_tag(tags, "title"),
            tags=_collect_tags(tags, "title"),
        ),
    )


def get_media_information(media_input: Path, logger: Logger) -> "Media":
    """Obtiene información del contenedor multimedia.

    Raises:
        UserError: Si el contenedor no tiene pista de vídeo.
        FfprobeError: Si ffprobe no puede leer el archivo.
        MissingParameterError: Si faltan parámetros requeridos.
    """
    data = _run_ffprobe(
        ["-show_format", "-show_streams", "-show_chapters"], media_input
    )
    logger.debug(msg=_("ffprobe media data: %(data)s"), data=data)

    video: Video | None = None
    audio: list[Audio] = []
    subtitles: list[Subtitles] = []
    video_track_index, audio_track_index, subtitles_track_index = 0, 0, 0

    for stream in to_dict_list(data.get("streams")):
        codec_type = stream.get("codec_type")
        tags = to_dict(stream.get("tags"))
        disposition = to_dict(stream.get("disposition"))

        if codec_type == "video":
            video = Video(
                path=media_input.absolute(),
                global_index=to_int(stream.get("index")),
                track_index=video_track_index,
                duration=_stream_duration(stream=stream, tags=tags),
                format=_build_video_format(stream=stream),
                metadata=_build_video_metadata(tags=tags),
                dispositions=_build_video_dispositions(disposition=disposition),
            )
            video_track_index += 1
        elif codec_type == "audio":
            audio.append(
                Audio(
                    path=media_input.absolute(),
                    global_index=to_int(stream.get("index")),
                    track_index=audio_track_index,
                    duration=_stream_duration(stream=stream, tags=tags),
                    format=_build_audio_format(stream=stream),
                    loudness=_build_audio_loudness(tags=tags),
                    metadata=_build_audio_metadata(tags=tags),
                    dispositions=_build_audio_dispositions(disposition=disposition),
                )
            )
            audio_track_index += 1
        elif codec_type == "subtitle":
            subtitles.append(
                Subtitles(
                    path=media_input.absolute(),
                    global_index=to_int(stream.get("index")),
                    track_index=subtitles_track_index,
                    duration=_stream_duration(stream=stream, tags=tags),
                    format=_build_subtitles_format(stream=stream),
                    metadata=_build_subtitles_metadata(tags=tags),
                    dispositions=_build_subtitles_dispositions(disposition=disposition),
                )
            )
            subtitles_track_index += 1

    if video is None:
        raise UserError(
            msg=_("Invalid video container: %(path)s") % {"path": str(media_input)}
        )

    fmt = to_dict(data.get("format"))
    tags = to_dict(fmt.get("tags"))
    duration = to_timedelta(to_float(fmt.get("duration")))
    chapters = [_build_chapter(chapter=ch) for ch in to_dict_list(data.get("chapters"))]

    try:
        media = Media(
            path=media_input.absolute(),
            duration=duration,
            format=_build_media_format(fmt=fmt),
            video=video,
            audio=audio or None,
            subtitles=subtitles or None,
            chapters=chapters or None,
            metadata=_build_media_metadata(tags=tags),
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

    for stream in to_dict_list(data.get("streams")):
        codec_type = stream.get("codec_type")
        tags = to_dict(stream.get("tags"))
        disposition = to_dict(stream.get("disposition"))

        if codec_type == "audio":
            audio.append(
                Audio(
                    path=audio_input.absolute(),
                    global_index=to_int(stream.get("index")),
                    track_index=audio_track_index,
                    duration=_stream_duration(stream=stream, tags=tags),
                    format=_build_audio_format(stream=stream),
                    loudness=_build_audio_loudness(tags=tags),
                    metadata=_build_audio_metadata(tags=tags),
                    dispositions=_build_audio_dispositions(disposition=disposition),
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

    format_name = to_text(to_dict(data.get("format")).get("format_name")) or ""
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
