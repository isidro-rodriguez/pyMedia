"""Pruebas de ffprobe: códecs desconocidos y salidas incompletas o mal formadas."""

import subprocess
from datetime import timedelta
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from pymedia import ffprobe
from pymedia.data.video_codecs import VIDEO_CODECS
from pymedia.errors import FfprobeError, UserError
from pymedia.logger import Logger
from pymedia.models.media import Media
from pymedia.utils import parse_duration

VIDEO: dict[str, Any] = {"index": 0, "codec_type": "video", "codec_name": "h264"}
NOT_DICTS = [None, [], "texto", 5]
UNKNOWN = "codec_inventado"


def _probe(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, data: dict[str, Any]
) -> Media:
    monkeypatch.setattr(ffprobe, "_run_ffprobe", lambda *_a, **_k: data)
    return ffprobe.get_media_information(tmp_path / "a.mkv", Logger.load())


def _data(*streams: dict[str, Any], **extra: Any) -> dict[str, Any]:
    return {"streams": list(streams), "format": {"duration": "10"}, **extra}


# --- Duraciones ---------------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    [
        None,
        "",
        "  ",
        "abc",
        "1:2",
        "aa:bb:cc",
        "1:99:00",
        "-5",
        "nan",
        "inf",
        "1e400",
        5,
    ],
)
def test_parse_duration_invalid_returns_none(value: object) -> None:
    """Una duración ausente o mal formada devuelve None sin lanzar."""
    assert parse_duration(value) is None


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("12.5", timedelta(seconds=12.5)),
        ("00:01:30.5", timedelta(seconds=90.5)),
        ("1:02:03", timedelta(hours=1, minutes=2, seconds=3)),
    ],
)
def test_parse_duration_valid(value: str, expected: timedelta) -> None:
    """Se aceptan segundos y el formato HH:MM:SS.ffffff."""
    assert parse_duration(value) == expected


def test_invalid_stream_duration_does_not_break_probe(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Una duración de stream inválida deja duration en None."""
    stream = {**VIDEO, "duration": "xx", "tags": {"DURATION": "99:99:99"}}
    media = _probe(monkeypatch, tmp_path, _data(stream))
    assert media.video is not None
    assert media.video.duration is None


def test_invalid_format_duration(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Una duración de contenedor inválida o infinita deja duration en None."""
    for bad in ("abc", "inf", "nan", None):
        data = {"streams": [VIDEO], "format": {"duration": bad}}
        assert _probe(monkeypatch, tmp_path, data).duration is None


# --- Estructura del JSON -----------------------------------------------------


@pytest.mark.parametrize("bad", NOT_DICTS)
def test_tags_not_a_dict(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, bad: object
) -> None:
    """Etiquetas y disposiciones que no son dict se tratan como vacías."""
    streams = [
        {**VIDEO, "tags": bad, "disposition": bad},
        {"index": 1, "codec_type": "audio", "tags": bad, "disposition": bad},
        {"index": 2, "codec_type": "subtitle", "tags": bad, "disposition": bad},
    ]
    data = {"streams": streams, "format": {"tags": bad}, "chapters": [{"tags": bad}]}

    media = _probe(monkeypatch, tmp_path, data)

    assert media.metadata.title is None
    assert media.metadata.tags == {}
    assert media.audio is not None
    assert media.audio[0].metadata.tags == {}
    assert media.audio[0].dispositions.default is False
    assert media.chapters is not None
    assert media.chapters[0].metadata.title is None


def test_missing_format(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Sin bloque 'format' el medio se construye con todo a None."""
    media = _probe(monkeypatch, tmp_path, {"streams": [VIDEO]})
    assert media.duration is None
    assert media.format.name is None
    assert media.format.size is None


@pytest.mark.parametrize("bad", NOT_DICTS)
def test_format_not_a_dict(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, bad: object
) -> None:
    """Un 'format' que no es dict se trata como ausente."""
    media = _probe(monkeypatch, tmp_path, {"streams": [VIDEO], "format": bad})
    assert media.format.name is None


@pytest.mark.parametrize("bad", [None, "x", 5, {}])
def test_missing_streams_media(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, bad: object
) -> None:
    """Sin streams válidos no hay pista de vídeo y se informa con UserError."""
    with pytest.raises(UserError):
        _probe(monkeypatch, tmp_path, {"streams": bad, "format": {}})


def test_missing_streams_key(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Ausencia total de la clave 'streams' en medios y en audio."""
    with pytest.raises(UserError):
        _probe(monkeypatch, tmp_path, {"format": {}})
    monkeypatch.setattr(ffprobe, "_run_ffprobe", lambda *_a, **_k: {})
    with pytest.raises(UserError):
        ffprobe.get_audio_information(tmp_path / "a.mka", Logger.load())


def test_non_dict_streams_are_skipped(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Los elementos de 'streams' que no son dict se ignoran."""
    data = {"streams": [None, "x", VIDEO], "format": {}}
    media = _probe(monkeypatch, tmp_path, data)
    assert media.video is not None


# --- codec_name --------------------------------------------------------------


@pytest.mark.parametrize("codec", [None, "", 5, ["h264"]])
def test_codec_name_missing_or_invalid(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, codec: object
) -> None:
    """codec_name ausente o de tipo incorrecto deja el códec en None."""
    streams = [
        {"index": 0, "codec_type": "video", "codec_name": codec},
        {"index": 1, "codec_type": "audio", "codec_name": codec},
        {"index": 2, "codec_type": "subtitle", "codec_name": codec},
    ]
    media = _probe(monkeypatch, tmp_path, _data(*streams))

    assert media.video is not None
    assert media.video.format.codec is None
    assert media.audio is not None
    assert media.audio[0].format.codec is None
    assert media.subtitles is not None
    assert media.subtitles[0].format.codec is None
    assert media.subtitles[0].format.is_text_based is None


def test_unknown_video_codec_falls_back_to_raw_name(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Un códec de vídeo fuera de VIDEO_CODECS conserva el nombre de ffprobe."""
    media = _probe(monkeypatch, tmp_path, _data({**VIDEO, "codec_name": UNKNOWN}))
    assert media.video is not None
    assert media.video.format.codec == UNKNOWN


def test_known_video_codec_uses_catalog_name(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Un códec de vídeo del catálogo usa su nombre normalizado."""
    media = _probe(monkeypatch, tmp_path, _data(VIDEO))
    assert media.video is not None
    assert media.video.format.codec == VIDEO_CODECS["h264"].name


def test_unknown_audio_codec_is_kept(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Un códec de audio desconocido se conserva tal cual en el modelo."""
    stream = {"index": 0, "codec_type": "audio", "codec_name": UNKNOWN}
    monkeypatch.setattr(ffprobe, "_run_ffprobe", lambda *_a, **_k: _data(stream))

    audio = ffprobe.get_audio_information(tmp_path / "a.mka", Logger.load())

    assert audio[0].format.codec == UNKNOWN


def test_unknown_subtitles_codec_has_no_derived_data(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Un códec de subtítulos desconocido deja mimetype e is_text_based en None."""
    stream = {"index": 1, "codec_type": "subtitle", "codec_name": UNKNOWN}
    media = _probe(monkeypatch, tmp_path, _data(VIDEO, stream))

    assert media.subtitles is not None
    fmt = media.subtitles[0].format
    assert (fmt.codec, fmt.mimetype, fmt.is_text_based) == (UNKNOWN, None, None)


# --- Campos numéricos --------------------------------------------------------


def test_malformed_numeric_fields(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Enteros, fracciones y tamaños mal formados quedan en None."""
    video = {
        **VIDEO,
        "index": "x",
        "width": "ancho",
        "height": [],
        "bit_rate": "N/A",
        "avg_frame_rate": "0/0",
    }
    audio = {
        "index": "y",
        "codec_type": "audio",
        "channels": "dos",
        "sample_rate": "abc",
        "bit_rate": None,
    }
    data = _data(video, audio)
    data["format"] = {"size": "grande", "bit_rate": "N/A", "nb_streams": "?"}

    media = _probe(monkeypatch, tmp_path, data)

    assert media.video is not None
    v = media.video
    assert (v.global_index, v.format.width, v.format.height) == (None, None, None)
    assert (v.format.bit_rate, v.format.fps) == (None, None)
    assert media.audio is not None
    a = media.audio[0]
    assert (a.global_index, a.format.channels, a.format.sample_rate) == (None,) * 3
    assert media.format.size is None
    assert media.format.nb_streams is None


def test_malformed_disposition_values(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Disposiciones con valores no numéricos cuentan como falsas."""
    stream = {**VIDEO, "disposition": {"default": "x", "forced": "1"}}
    media = _probe(monkeypatch, tmp_path, _data(stream))
    assert media.video is not None
    assert media.video.dispositions.default is False
    assert media.video.dispositions.forced is True


@pytest.mark.parametrize("raw", ["", " ", "dB", "abc dB", None])
def test_malformed_loudness_tags(raw: str | None) -> None:
    """ReplayGain y R128 mal formados producen None, sin IndexError."""
    tags = {"REPLAYGAIN_TRACK_GAIN": raw, "REPLAYGAIN_TRACK_PEAK": raw}
    tags["R128_TRACK_GAIN"] = raw
    loudness = ffprobe._build_audio_loudness(tags)
    assert loudness.replaygain_gain is None
    assert loudness.replaygain_peak is None
    assert loudness.integrated is None


def test_valid_loudness_tags() -> None:
    """Las etiquetas correctas se convierten a números."""
    tags = {
        "REPLAYGAIN_TRACK_GAIN": "-3.50 dB",
        "REPLAYGAIN_TRACK_PEAK": "0.98",
        "R128_TRACK_GAIN": "256",
    }
    loudness = ffprobe._build_audio_loudness(tags)
    assert loudness.replaygain_gain == -3.5
    assert loudness.replaygain_peak == 0.98
    assert loudness.integrated == -22.0


# --- Capítulos ---------------------------------------------------------------


@pytest.mark.parametrize("time_base", ["1/0", "abc", "", "1/1000/2", "/1000", None, 5])
def test_invalid_time_base(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, time_base: object
) -> None:
    """Un time_base inválido (incl. denominador 0) anula solo start/end crudos."""
    chapter = {
        "id": 1,
        "time_base": time_base,
        "start": 0,
        "end": 1000,
        "start_time": "0.0",
        "end_time": "1.0",
    }
    media = _probe(monkeypatch, tmp_path, _data(VIDEO, chapters=[chapter]))

    assert media.chapters is not None
    ch = media.chapters[0]
    assert ch.format.start is None
    assert ch.format.end is None
    assert ch.end_time == timedelta(seconds=1)


def test_valid_time_base(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Con time_base válido, start/end se escalan a timedelta."""
    chapter = {"id": 1, "time_base": "1/1000", "start": 1500, "end": "3000"}
    media = _probe(monkeypatch, tmp_path, _data(VIDEO, chapters=[chapter]))

    assert media.chapters is not None
    assert media.chapters[0].format.start == timedelta(seconds=1.5)
    assert media.chapters[0].format.end == timedelta(seconds=3)


def test_incomplete_chapters(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Capítulos incompletos se conservan con campos None; los no dict se ignoran."""
    chapters = [{}, {"id": 2}, {"start": 1000}, "x", None, {"id": "z", "start": "a"}]
    media = _probe(monkeypatch, tmp_path, _data(VIDEO, chapters=chapters))

    assert media.chapters is not None
    assert len(media.chapters) == 4
    for ch in media.chapters:
        assert ch.start_time is None
        assert ch.end_time is None
        assert ch.format.start is None
        assert ch.metadata.title is None
    assert [ch.id for ch in media.chapters] == [None, 2, None, None]


@pytest.mark.parametrize("bad", [None, "x", 5, {}])
def test_chapters_not_a_list(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, bad: object
) -> None:
    """Un bloque 'chapters' inválido equivale a no tener capítulos."""
    media = _probe(monkeypatch, tmp_path, _data(VIDEO, chapters=bad))
    assert media.chapters is None


# --- Salida cruda de ffprobe -------------------------------------------------


@pytest.mark.parametrize("stdout", ["", "no es json", "[]", "5", "null"])
def test_run_ffprobe_invalid_output(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, stdout: str
) -> None:
    """Una salida vacía, no JSON o no objeto se informa como FfprobeError."""
    monkeypatch.setattr(
        subprocess, "run", lambda *_a, **_k: SimpleNamespace(stdout=stdout)
    )
    with pytest.raises(FfprobeError):
        ffprobe._run_ffprobe([], tmp_path / "a.mkv")
