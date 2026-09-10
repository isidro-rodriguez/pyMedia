"""Tests del modelo de configuración `Config` y su validación."""

from pathlib import Path
from unittest.mock import patch

import pytest

from pymedia.errors import ConfigError
from pymedia.models.config import Config, Transcode, TranscodePreset

_DEFAULT_CONFIG = """\
[app]
language = "system"
stall_timeout = 60

[default_containers]
animated_image = ".gif"
audio_track = ".m4a"
image = ".jpg"
media = ".mp4"
subtitles = ".srt"

[transcode.fast]
video_codec = "h265"
video_preset = "veryfast"
video_crf = 25
audio_codec = "aac"
audio_bit_rate = "160k"

[transcode.even]
video_codec = "h265"
video_preset = "medium"
video_crf = 23
audio_codec = "aac"
audio_bit_rate = "192k"

[transcode.slow]
video_codec = "h265"
video_preset = "slower"
video_crf = 20
audio_codec = "aac"
audio_bit_rate = "256k"
"""


def _load(text: str, tmp_path: Path) -> Config:
    """Carga `text` como `config.toml` del usuario en un directorio temporal."""
    (tmp_path / "config.toml").write_text(text, encoding="utf-8")
    with patch("platformdirs.user_config_dir", return_value=str(tmp_path)):
        return Config.load()


def test_load_carga_perfiles_y_valores_por_defecto(tmp_path: Path) -> None:
    """Un `config.toml` válido expone los tres perfiles `transcode`."""
    config = _load(_DEFAULT_CONFIG, tmp_path)

    assert isinstance(config.transcode, TranscodePreset)
    assert isinstance(config.transcode.fast, Transcode)
    assert config.transcode.fast.video_crf == 25
    assert config.transcode.even.video_preset == "medium"
    assert config.transcode.slow.audio_bit_rate == "256k"
    assert config.default_containers.media == ".mp4"
    assert config.app.language == "system"
    assert config.app.stall_timeout == 60


def test_load_crea_config_por_defecto_si_no_existe(tmp_path: Path) -> None:
    """Sin `config.toml` del usuario, `load` copia la plantilla de `resources`."""
    with patch("platformdirs.user_config_dir", return_value=str(tmp_path)):
        config = Config.load()

    assert (tmp_path / "config.toml").exists()
    assert config.transcode.fast.video_codec == "h265"


def test_load_eleva_error_si_falta_un_perfil(tmp_path: Path) -> None:
    """La ausencia de un perfil declarado en `PresetsTranscodeMode` es inválida."""
    slow_block = (
        "[transcode.slow]\n"
        'video_codec = "h265"\n'
        'video_preset = "slower"\n'
        "video_crf = 20\n"
        'audio_codec = "aac"\n'
        'audio_bit_rate = "256k"\n'
    )
    text = _DEFAULT_CONFIG.replace(slow_block, "")

    with pytest.raises(ConfigError, match="transcode presets"):
        _load(text, tmp_path)


def test_load_error_perfil_desconocido(tmp_path: Path) -> None:
    """Un perfil extra en `[transcode]` es inválido y reporta el conjunto esperado."""
    text = _DEFAULT_CONFIG.replace("[transcode.slow]", "[transcode.maximum]")

    with pytest.raises(ConfigError, match="transcode presets"):
        _load(text, tmp_path)


def test_load_error_perfil_no_es_tabla(tmp_path: Path) -> None:
    """Un perfil que no es una tabla produce un `ConfigError` claro."""
    text = _DEFAULT_CONFIG.replace(
        "[transcode.fast]\n"
        'video_codec = "h265"\n'
        'video_preset = "veryfast"\n'
        "video_crf = 25\n"
        'audio_codec = "aac"\n'
        'audio_bit_rate = "160k"\n',
        '[transcode]\nfast = "h265"\n',
    )

    with pytest.raises(ConfigError, match="expected to be a table"):
        _load(text, tmp_path)


@pytest.mark.parametrize(
    ("invalido", "replacement", "fragmento"),
    [
        ('video_codec = "h265"', 'video_codec = "mpeg"', "transcode.fast.video_codec"),
        (
            'video_preset = "veryfast"',
            'video_preset = "inexistente"',
            "transcode.fast.video_preset",
        ),
        ("video_crf = 25", "video_crf = 999", "transcode.fast.video_crf"),
        ("video_crf = 25", 'video_crf = "25"', "transcode.fast.video_crf"),
        ('audio_codec = "aac"', 'audio_codec = "ogg"', "transcode.fast.audio_codec"),
        (
            'audio_bit_rate = "160k"',
            'audio_bit_rate = "100k"',
            "transcode.fast.audio_bit_rate",
        ),
    ],
)
def test_load_error_campo_invalido(
    invalido: str, replacement: str, fragmento: str, tmp_path: Path
) -> None:
    """Un parámetro de un perfil fuera de los valores admitidos eleva `ConfigError`."""
    text = _DEFAULT_CONFIG.replace(invalido, replacement, 1)

    with pytest.raises(ConfigError, match=fragmento):
        _load(text, tmp_path)


@pytest.mark.parametrize(
    ("invalido", "replacement", "fragmento"),
    [
        ('media = ".mp4"', 'media = ".webm"', "default_container.media"),
        ('language = "system"', 'language = "klingon"', "app.language"),
        ("stall_timeout = 60", "stall_timeout = 0", "app.stall_timeout"),
        ("stall_timeout = 60", 'stall_timeout = "60"', "app.stall_timeout"),
    ],
)
def test_demandada_opciones_invalidas(
    invalido: str, replacement: str, fragmento: str, tmp_path: Path
) -> None:
    """Valores no admitidos en contenedores, idioma y timeout elevan `ConfigError`."""
    text = _DEFAULT_CONFIG.replace(invalido, replacement, 1)

    with pytest.raises(ConfigError, match=fragmento):
        _load(text, tmp_path)
