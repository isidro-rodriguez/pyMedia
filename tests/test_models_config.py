"""Tests para la validación del fichero de configuración (pymedia.models.config)."""

import tomllib
from importlib.resources import files

import pytest

from pymedia.errors import InvalidConfigError
from pymedia.models.config import Config


@pytest.fixture
def default_config() -> dict:
    """Carga el config.toml por defecto desde los recursos."""
    return tomllib.loads(
        files("pymedia.resources").joinpath("config.toml").read_text(encoding="utf-8")
    )


def _with_encode(data: dict, **kwargs) -> dict:
    """Devuelve una copia del config con los campos de [encode] modificados."""
    result = dict(data)
    result["encode"] = dict(data["encode"], **kwargs)
    return result


def _with_conflictive_join(data: dict, **kwargs) -> dict:
    """Devuelve una copia con los campos de [conflictive_join] modificados."""
    result = dict(data)
    result["conflictive_join"] = dict(data["conflictive_join"], **kwargs)
    return result


# -----------------------------------------------------------------------------
#  Config por defecto
# -----------------------------------------------------------------------------


def test_default_config_is_valid(default_config):
    Config._validate(default_config)


# -----------------------------------------------------------------------------
#  encode.video_codec
# -----------------------------------------------------------------------------


def test_video_codec_valid_values(default_config):
    # Cada codec tiene presets y rango de crf propios
    cases = {
        "av1": {"video_preset": "0", "video_crf": 32},
        "h264": {"video_preset": "fast", "video_crf": 22},
        "h265": {"video_preset": "slow", "video_crf": 24},
        "hevc": {"video_preset": "slow", "video_crf": 24},
    }
    for codec, extra in cases.items():
        Config._validate(_with_encode(default_config, video_codec=codec, **extra))


def test_video_codec_invalid(default_config):
    with pytest.raises(InvalidConfigError, match="encode.video_codec"):
        Config._validate(_with_encode(default_config, video_codec="xxx"))


# -----------------------------------------------------------------------------
#  encode.video_preset
# -----------------------------------------------------------------------------


def test_video_preset_valid(default_config):
    Config._validate(_with_encode(default_config, video_preset="slow"))


def test_video_preset_invalid(default_config):
    with pytest.raises(InvalidConfigError, match="encode.video_preset"):
        Config._validate(_with_encode(default_config, video_preset="nope"))


# -----------------------------------------------------------------------------
#  encode.video_crf
# -----------------------------------------------------------------------------


def test_video_crf_valid(default_config):
    Config._validate(_with_encode(default_config, video_crf=22))


def test_video_crf_invalid(default_config):
    with pytest.raises(InvalidConfigError, match="encode.video_crf"):
        Config._validate(_with_encode(default_config, video_crf=999))


# -----------------------------------------------------------------------------
#  encode.audio_codec
# -----------------------------------------------------------------------------


def test_audio_codec_valid_values(default_config):
    # Cada codec tiene bit_rates y containers propios
    cases = {
        "aac": {"audio_bit_rate": "160k", "default_container": ".mp4"},
        "eac3": {"audio_bit_rate": "192k", "default_container": ".ts"},
        "opus": {"audio_bit_rate": "128k", "default_container": ".mkv"},
    }
    for codec, extra in cases.items():
        Config._validate(_with_encode(default_config, audio_codec=codec, **extra))


def test_audio_codec_invalid(default_config):
    with pytest.raises(InvalidConfigError, match="encode.audio_codec"):
        Config._validate(_with_encode(default_config, audio_codec="xxx"))


# -----------------------------------------------------------------------------
#  encode.audio_bit_rate
# -----------------------------------------------------------------------------


def test_audio_bit_rate_valid(default_config):
    Config._validate(_with_encode(default_config, audio_bit_rate="160k"))


def test_audio_bit_rate_invalid(default_config):
    with pytest.raises(InvalidConfigError, match="encode.audio_bit_rate"):
        Config._validate(_with_encode(default_config, audio_bit_rate="999k"))


# -----------------------------------------------------------------------------
#  encode.default_container
# -----------------------------------------------------------------------------


def test_default_container_valid(default_config):
    Config._validate(_with_encode(default_config, default_container=".mp4"))


def test_default_container_invalid(default_config):
    with pytest.raises(InvalidConfigError, match="encode.default_container"):
        Config._validate(_with_encode(default_config, default_container=".xyz"))


# -----------------------------------------------------------------------------
#  conflictive_join.resize_to
# -----------------------------------------------------------------------------


def test_resize_to_valid_values(default_config):
    for value in ("max_height", "min_height"):
        Config._validate(_with_conflictive_join(default_config, resize_to=value))


def test_resize_to_invalid(default_config):
    with pytest.raises(InvalidConfigError, match="conflictive_join.resize_to"):
        Config._validate(_with_conflictive_join(default_config, resize_to="bad"))


# -----------------------------------------------------------------------------
#  conflictive_join.fps
# -----------------------------------------------------------------------------


def test_fps_valid_values(default_config):
    for value in ("max_fps", "min_fps"):
        Config._validate(_with_conflictive_join(default_config, fps=value))


def test_fps_invalid(default_config):
    with pytest.raises(InvalidConfigError, match="conflictive_join.fps"):
        Config._validate(_with_conflictive_join(default_config, fps="bad"))


# -----------------------------------------------------------------------------
#  conflictive_join.channels
# -----------------------------------------------------------------------------


def test_channels_valid_values(default_config):
    for value in ("mono", "stereo", "5.1"):
        Config._validate(_with_conflictive_join(default_config, channels=value))


def test_channels_invalid(default_config):
    with pytest.raises(InvalidConfigError, match="conflictive_join.channels"):
        Config._validate(_with_conflictive_join(default_config, channels="bad"))


# -----------------------------------------------------------------------------
#  Múltiples errores
# -----------------------------------------------------------------------------


def test_multiple_errors_collected(default_config):
    bad = _with_encode(
        default_config,
        video_codec="xxx",
        video_preset="nope",
        video_crf=999,
        audio_codec="yyy",
        audio_bit_rate="999k",
        default_container=".xyz",
    )
    bad = _with_conflictive_join(bad, resize_to="bad", fps="bad", channels="bad")

    with pytest.raises(InvalidConfigError) as exc_info:
        Config._validate(bad)

    message = exc_info.value.message
    # Los codecs inválidos omiten las validaciones dependientes
    assert "encode.video_codec" in message
    assert "encode.audio_codec" in message
    assert "conflictive_join.resize_to" in message
    assert "conflictive_join.fps" in message
    assert "conflictive_join.channels" in message
