"""Tests de `--delay`: desfase de pistas de audio y subtítulos sin recodificar.

Se ejecuta ffmpeg de verdad y se miden las marcas de tiempo del resultado.
"""

import subprocess
from pathlib import Path

import pytest
from helpers import Invoke, stream_codec_names, stream_types

from pymedia.mixins.delay_mixin import DelayMixin


def _first_pts(path: Path, stream: str) -> float:
    """Marca de tiempo del primer paquete de la pista indicada (`a:1`, `s:0`)."""
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            stream,
            "-show_entries",
            "packet=pts_time",
            "-read_intervals",
            "%+#1",
            "-of",
            "csv=p=0",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(result.stdout.split()[0])


# =============================================================================
#  Composición
# =============================================================================


@pytest.mark.parametrize(
    ("delay", "itsoffset", "setts"),
    [
        (0.5, "0.5", "setts=ts=TS+0.5/TB"),
        (-1.25, "-1.25", "setts=ts=TS-1.25/TB"),
        (2.0, "2", "setts=ts=TS+2/TB"),
        (0.1234, "0.123", "setts=ts=TS+0.123/TB"),
    ],
)
def test_delay_commands(delay: float, itsoffset: str, setts: str) -> None:
    """El desfase se expresa en segundos con precisión de milisegundo."""
    mixin = DelayMixin()
    mixin.create_delay(delay=delay)

    assert mixin.to_delay_input_cmd() == ["-itsoffset", itsoffset]
    assert mixin.to_delay_stream_cmd("a:1") == ["-bsf:a:1", setts]


@pytest.mark.parametrize("delay", [None, 0.0])
def test_no_delay_adds_nothing(delay: float | None) -> None:
    """Sin desfase (o con 0) no se añade ninguna opción."""
    mixin = DelayMixin()
    mixin.create_delay(delay=delay)

    assert mixin.to_delay_input_cmd() == []
    assert mixin.to_delay_stream_cmd("s:0") == []


# =============================================================================
#  Pistas del contenedor (edit-audio, edit-subs)
# =============================================================================


@pytest.mark.parametrize("delay", ["0.5", "-0.5"])
def test_edit_audio_delay_shifts_only_that_track(
    pymedia: Invoke, video_mkv_two_audio: Path, tmp_path: Path, delay: str
) -> None:
    """Solo se desplaza la pista indicada; el orden de pistas no cambia."""
    output = tmp_path / "out.mkv"

    result = pymedia(
        "edit-audio",
        str(video_mkv_two_audio),
        "--track",
        "1",
        "--delay",
        delay,
        "-o",
        str(output),
    )

    assert result.exit_code == 0, result.output
    assert stream_types(output) == stream_types(video_mkv_two_audio)
    shift = _first_pts(output, "a:1") - _first_pts(output, "a:0")
    assert shift == pytest.approx(float(delay), abs=0.05)


def test_edit_subs_delay(pymedia: Invoke, video_mkv_subs: Path, tmp_path: Path) -> None:
    """Los subtítulos se retrasan sin recodificar."""
    output = tmp_path / "out.mkv"

    result = pymedia(
        "edit-subs",
        str(video_mkv_subs),
        "--track",
        "0",
        "--delay",
        "0.75",
        "-o",
        str(output),
    )

    assert result.exit_code == 0, result.output
    # Relativo a la otra pista: el muxer puede desplazar todo el contenedor.
    before = _first_pts(video_mkv_subs, "s:0") - _first_pts(video_mkv_subs, "s:1")
    after = _first_pts(output, "s:0") - _first_pts(output, "s:1")
    assert after - before == pytest.approx(0.75, abs=0.01)


def test_edit_subs_negative_delay_requires_matroska(
    pymedia: Invoke, video_mkv_subs: Path, tmp_path: Path
) -> None:
    """MP4 deforma los subtítulos adelantados al copiarlos: se rechaza."""
    result = pymedia(
        "edit-subs",
        str(video_mkv_subs),
        "--track",
        "0",
        "--delay",
        "-0.5",
        "-o",
        str(tmp_path / "out.mp4"),
        "--show-cmd",
    )

    assert result.exit_code != 0
    assert "Matroska" in result.output


@pytest.mark.parametrize("name", ["edit-audio", "edit-subs"])
def test_edit_delay_alone_is_enough(
    pymedia: Invoke, video_mkv_subs: Path, video_mkv_two_audio: Path, name: str
) -> None:
    """`--delay` basta como única edición de la pista."""
    media = video_mkv_two_audio if name == "edit-audio" else video_mkv_subs

    result = pymedia(name, str(media), "--track", "0", "--delay", "1", "--show-cmd")

    assert result.exit_code == 0, result.output
    assert "setts=ts=TS+1/TB" in result.output


# =============================================================================
#  Ficheros externos (add-audio, add-subs)
# =============================================================================


def test_add_audio_delay(
    pymedia: Invoke, video_mkv: Path, audio_m4a: Path, tmp_path: Path
) -> None:
    """El audio importado empieza con el desfase indicado."""
    output = tmp_path / "out.mkv"

    result = pymedia(
        "add-audio", str(video_mkv), str(audio_m4a), "--delay", "0.3", "-o", str(output)
    )

    assert result.exit_code == 0, result.output
    assert stream_codec_names(output, "audio") == ["aac", "aac"]
    assert _first_pts(output, "a:1") == pytest.approx(0.3, abs=0.05)


def test_add_subs_delay(
    pymedia: Invoke, video_mkv: Path, subs_spa: Path, tmp_path: Path
) -> None:
    """Los subtítulos importados se desplazan, también hacia atrás si caben."""
    output = tmp_path / "out.mkv"

    result = pymedia(
        "add-subs",
        str(video_mkv),
        str(subs_spa),
        "--language",
        "spa",
        "--delay",
        "0.5",
        "-o",
        str(output),
    )

    assert result.exit_code == 0, result.output
    assert _first_pts(output, "s:0") == pytest.approx(0.5, abs=0.01)
