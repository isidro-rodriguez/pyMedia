"""Tests unitarios de gif_cmd que verifican la estructura del comando."""

from datetime import timedelta
from pathlib import Path

import pytest

from pymedia.cli_params import GyrateMode, ScaleGifMode
from pymedia.domain.encode_pipeline import EncodePipeline
from pymedia.domain.media_input import MediaInput, Video
from pymedia.ffmpeg.gif_cmd import gif_cmd


def _media(video: Video | None = None) -> MediaInput:
    """Crea un MediaInput de prueba."""
    return MediaInput(
        path=Path("video.mp4"),
        duration=timedelta(seconds=10),
        video=video,
    )


def _video(width: int = 640, height: int = 360) -> Video:
    """Crea un Video de prueba."""
    return Video(width=width, height=height)


def _pipeline(**kwargs) -> EncodePipeline:
    """Crea un EncodePipeline con parámetros opcionales."""
    return EncodePipeline(**kwargs)


def _get_filter_complex(cmd: list[str]) -> str:
    """Extrae el valor de -filter_complex del comando."""
    idx = cmd.index("-filter_complex")
    return cmd[idx + 1]


# ─────────────────────── scale con enum ────────────────────────


def test_gif_cmd_scale_enum_converted_to_int() -> None:
    """ScaleGifMode.P480 se resuelve a 480 en el filtro, no a 'ScaleGifMode.P480'."""
    cmd = gif_cmd(
        Path("video.mp4"),
        _pipeline(scale=ScaleGifMode.P480),
        _media(_video()),
        fps=15,
    )
    filters = _get_filter_complex(cmd)
    assert "scale=-2:480" in filters
    assert "ScaleGifMode" not in filters


def test_gif_cmd_scale_int_value() -> None:
    """Un int normal funciona correctamente como scale."""
    cmd = gif_cmd(
        Path("video.mp4"),
        _pipeline(scale=240),
        _media(_video()),
        fps=15,
    )
    filters = _get_filter_complex(cmd)
    assert "scale=-2:240" in filters


# ─────────────────── flags=lanczos en scale ────────────────────


def test_gif_cmd_flags_lanczos_inside_scale() -> None:
    """flags=lanczos va dentro del filtro scale, no como sub-opción global."""
    cmd = gif_cmd(
        Path("video.mp4"),
        _pipeline(scale=ScaleGifMode.P480),
        _media(_video()),
        fps=15,
    )
    filters = _get_filter_complex(cmd)
    assert "scale=-2:480:flags=lanczos" in filters


def test_gif_cmd_no_flags_without_scale() -> None:
    """Sin scale, no aparece flags=lanczos en el filtro."""
    cmd = gif_cmd(
        Path("video.mp4"),
        _pipeline(),
        _media(_video()),
        fps=15,
    )
    filters = _get_filter_complex(cmd)
    assert "flags=lanczos" not in filters


# ─────────────────── sin comillas literales ────────────────────


def test_gif_cmd_no_literal_quotes_in_filter() -> None:
    """El filter_complex no contiene comillas dobles literales."""
    cmd = gif_cmd(
        Path("video.mp4"),
        _pipeline(scale=ScaleGifMode.P480),
        _media(_video()),
        fps=15,
    )
    filters = _get_filter_complex(cmd)
    assert not filters.startswith('"')
    assert not filters.endswith('"')
    assert '"' not in filters


# ─────────────────────── estructura base ───────────────────────


def test_gif_cmd_basic_structure() -> None:
    """Estructura mínima del comando sin opciones extra."""
    cmd = gif_cmd(
        Path("video.mp4"),
        _pipeline(),
        _media(_video()),
        fps=15,
    )
    filters = _get_filter_complex(cmd)
    assert filters == (
        "fps=15,split[a][b];[a]palettegen[p];[b][p]paletteuse=dither=floyd_steinberg"
    )


def test_gif_cmd_default_fps() -> None:
    """Si fps es None, se usa 15 por defecto."""
    cmd = gif_cmd(
        Path("video.mp4"),
        _pipeline(),
        _media(_video()),
    )
    filters = _get_filter_complex(cmd)
    assert "fps=15" in filters


def test_gif_cmd_output_name() -> None:
    """El nombre de salida usa el stem del path + .gif."""
    cmd = gif_cmd(
        Path("video.mp4"),
        _pipeline(),
        _media(_video()),
        fps=15,
    )
    assert cmd[-1] == "video.gif"


def test_gif_cmd_custom_output_name() -> None:
    """Si output_name termina en .gif se usa tal cual."""
    cmd = gif_cmd(
        Path("video.mp4"),
        _pipeline(),
        _media(_video()),
        fps=15,
        output_name="custom.gif",
    )
    assert cmd[-1] == "custom.gif"


def test_gif_cmd_output_name_without_extension() -> None:
    """Si output_name no termina en .gif, se añade la extensión."""
    cmd = gif_cmd(
        Path("video.mp4"),
        _pipeline(),
        _media(_video()),
        fps=15,
        output_name="custom",
    )
    assert cmd[-1] == "custom.gif"


# ─────────────────────── crop ──────────────────────────────────


def test_gif_cmd_with_crop() -> None:
    """Crop genera el filtro crop con dimensiones correctas."""
    media = _media(_video(width=640, height=360))
    cmd = gif_cmd(
        Path("video.mp4"),
        _pipeline(crop="100,50,25,25"),
        media,
        fps=15,
    )
    filters = _get_filter_complex(cmd)
    # crop_w = 640 - 100 - 50 = 490, crop_h = 360 - 25 - 25 = 310
    assert "crop=490:310:100:25" in filters
    assert "flags=lanczos" not in filters


# ─────────────────────── gyrate ────────────────────────────────


@pytest.mark.parametrize(
    "gyrate,expected",
    [
        (90, "transpose=1"),
        (180, "vflip,hflip"),
        (270, "transpose=2"),
    ],
)
def test_gif_cmd_with_gyrate(gyrate: int, expected: str) -> None:
    """Gyrate genera el filtro de rotación correcto."""
    cmd = gif_cmd(
        Path("video.mp4"),
        _pipeline(gyrate=gyrate),
        _media(_video()),
        fps=15,
    )
    filters = _get_filter_complex(cmd)
    assert expected in filters
    assert "flags=lanczos" not in filters


def test_gif_cmd_gyrate_enum_works() -> None:
    """GyrateMode enum funciona correctamente con match."""
    cmd = gif_cmd(
        Path("video.mp4"),
        _pipeline(gyrate=GyrateMode.d90),
        _media(_video()),
        fps=15,
    )
    filters = _get_filter_complex(cmd)
    assert "transpose=1" in filters


# ─────────────────── input file (-i) ──────────────────────────


def test_gif_cmd_includes_input_file() -> None:
    """El comando incluye -i con la ruta del vídeo de entrada."""
    path = Path("video.mp4")
    cmd = gif_cmd(path, _pipeline(), _media(_video()), fps=15)
    assert "-i" in cmd
    idx = cmd.index("-i")
    assert cmd[idx + 1] == str(path)


def test_gif_cmd_input_before_filter_complex() -> None:
    """El -i aparece antes de -filter_complex en el comando."""
    cmd = gif_cmd(Path("video.mp4"), _pipeline(), _media(_video()), fps=15)
    i_idx = cmd.index("-i")
    fc_idx = cmd.index("-filter_complex")
    assert i_idx < fc_idx


# ─────────────────── start_point / end_point ───────────────────


def test_gif_cmd_start_point() -> None:
    """start_point añade -ss con el tiempo de inicio."""
    cmd = gif_cmd(
        Path("video.mp4"),
        _pipeline(),
        _media(_video()),
        fps=15,
        start_point="00:10",
    )
    assert "-ss" in cmd
    idx = cmd.index("-ss")
    assert cmd[idx + 1] == "0:00:10"


def test_gif_cmd_end_point() -> None:
    """end_point añade -to con el tiempo final (no usa start_point)."""
    cmd = gif_cmd(
        Path("video.mp4"),
        _pipeline(),
        _media(_video()),
        fps=15,
        end_point="00:20",
    )
    assert "-to" in cmd
    idx = cmd.index("-to")
    assert cmd[idx + 1] == "0:00:20"


def test_gif_cmd_start_and_end_point() -> None:
    """start_point y end_point generan -ss y -to."""
    cmd = gif_cmd(
        Path("video.mp4"),
        _pipeline(),
        _media(_video()),
        fps=15,
        start_point="00:10",
        end_point="00:20",
    )
    assert "-ss" in cmd
    assert "-to" in cmd
    ss_idx = cmd.index("-ss")
    to_idx = cmd.index("-to")
    assert cmd[ss_idx + 1] == "0:00:10"
    assert cmd[to_idx + 1] == "0:00:20"


# ─────────────── crop + scale combinados ───────────────────────


def test_gif_cmd_crop_and_scale() -> None:
    """Crop + scale generan ambos filtros con flags en scale."""
    media = _media(_video(width=640, height=360))
    cmd = gif_cmd(
        Path("video.mp4"),
        _pipeline(scale=ScaleGifMode.P240, crop="100,50,25,25"),
        media,
        fps=15,
    )
    filters = _get_filter_complex(cmd)
    assert "crop=490:310:100:25" in filters
    assert "scale=-2:240:flags=lanczos" in filters