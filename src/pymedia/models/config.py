import tomllib
from dataclasses import dataclass
from enum import Enum
from importlib.resources import files
from pathlib import Path

import platformdirs

from pymedia import locales
from pymedia.data.audio_codecs import AUDIO_CODECS
from pymedia.data.video_codecs import VIDEO_CODECS
from pymedia.errors import InvalidConfigError


class AudioCodec(Enum):
    """Lista de códecs de audio disponibles en esta aplicación."""

    AAC = "aac"
    EAC3 = "eac3"
    OPUS = "opus"


class Channels(Enum):
    """Refiere al uso de canales de audio en uniones conflictivas."""

    MONO = "mono"
    STEREO = "stereo"
    SURROUND = "5.1"


class Language(Enum):
    """Idiomas disponibles para la interfaz de la aplicación."""

    SYSTEM = "system"
    ENGLISH = "english"
    SPANISH = "spanish"
    ITALIAN = "italian"
    FRENCH = "french"


class ResizeTo(Enum):
    """Refiere la altura en que se redimensionan los vídeos en uniones conflictivas."""

    MAX_HEIGHT = "max_height"
    MIN_HEIGHT = "min_height"


class TargetFPS(Enum):
    """
    Refiere al FPS en el que se transcodificarán los vídeos en uniones conflictivas.
    """

    MAX_FPS = "max_fps"
    MIN_FPS = "min_fps"


class VideoCodec(Enum):
    """Lista de códecs de vídeo disponibles en esta aplicación."""

    AV1 = "av1"
    H264 = "h264"
    H265 = "h265"
    HEVC = "hevc"


@dataclass(frozen=True)
class Encode:
    video_codec: str
    video_preset: str
    video_crf: int
    audio_codec: str
    audio_bit_rate: str
    default_container: str


@dataclass(frozen=True)
class ConflictiveJoin:
    resize_to: str
    fps: str
    channels: str
    confirm_encode: bool


@dataclass(frozen=True)
class App:
    language: str
    disable_resolution_increase: bool


@dataclass(frozen=True)
class Config:
    encode: Encode
    conflictive_join: ConflictiveJoin
    app: App

    @classmethod
    def load(cls) -> "Config":
        path = (
            Path(platformdirs.user_config_dir("pymedia", appauthor=False, roaming=True))
            / "config.toml"
        )
        if not path.exists():
            cls._create(path)

        with path.open("rb") as f:
            data = tomllib.load(f)
            cls._validate(data)

        return cls(
            encode=Encode(**data["encode"]),
            conflictive_join=ConflictiveJoin(**data["conflictive_join"]),
            app=App(**data["app"]),
        )

    @classmethod
    def _create(cls, path: Path) -> None:
        """Copia el config por defecto desde los recursos a la ruta de usuario."""
        path.parent.mkdir(parents=True, exist_ok=True)
        src = (
            files("pymedia.resources")
            .joinpath("config.toml")
            .read_text(encoding="utf-8")
        )
        path.write_text(src, encoding="utf-8")

    @classmethod
    def _validate(cls, data: dict) -> None:
        """Valida los valores del config.toml."""
        errors: list[str] = []

        encode = data["encode"]
        conflictive_join = data["conflictive_join"]
        app = data["app"]

        # encode.video_codec
        video_codec = encode["video_codec"]
        valid_video_codecs = {v.value for v in VideoCodec}
        if video_codec not in valid_video_codecs:
            errors.append(
                locales.ConfigValidation["invalid_video_codec"].format(
                    expected=", ".join(sorted(valid_video_codecs))
                )
            )

        # encode.video_preset
        video_preset = encode["video_preset"]
        if video_codec in VIDEO_CODECS:
            presets = VIDEO_CODECS[video_codec].presets
            if presets is not None and video_preset not in presets:
                errors.append(
                    locales.ConfigValidation["invalid_video_preset"].format(
                        expected=", ".join(presets)
                    )
                )

        # encode.video_crf
        video_crf = encode["video_crf"]
        if video_codec in VIDEO_CODECS:
            crf = VIDEO_CODECS[video_codec].crf
            if crf is not None and not crf[0] <= video_crf <= crf[1]:
                errors.append(
                    locales.ConfigValidation["invalid_video_crf"].format(
                        min=crf[0], max=crf[1]
                    )
                )

        # encode.audio_codec
        audio_codec = encode["audio_codec"]
        valid_audio_codecs = {a.value for a in AudioCodec}
        if audio_codec not in valid_audio_codecs:
            errors.append(
                locales.ConfigValidation["invalid_audio_codec"].format(
                    expected=", ".join(sorted(valid_audio_codecs))
                )
            )

        # encode.audio_bit_rate
        audio_bit_rate = encode["audio_bit_rate"]
        if audio_codec in AUDIO_CODECS:
            bit_rates = AUDIO_CODECS[audio_codec].bit_rates
            if bit_rates is not None and audio_bit_rate not in bit_rates:
                errors.append(
                    locales.ConfigValidation["invalid_audio_bit_rate"].format(
                        expected=", ".join(bit_rates)
                    )
                )

        # encode.default_container
        default_container = encode["default_container"]
        if video_codec in VIDEO_CODECS and audio_codec in AUDIO_CODECS:
            video_containers = VIDEO_CODECS[video_codec].containers
            audio_containers = AUDIO_CODECS[audio_codec].containers
            if (
                default_container not in video_containers
                or default_container not in audio_containers
            ):
                common = sorted(set(video_containers) & set(audio_containers))
                errors.append(
                    locales.ConfigValidation["invalid_default_container"].format(
                        expected=", ".join(common)
                    )
                )

        # conflictive_join.resize_to
        resize_to = conflictive_join["resize_to"]
        valid_resize_to = {r.value for r in ResizeTo}
        if resize_to not in valid_resize_to:
            errors.append(
                locales.ConfigValidation["invalid_resize_to"].format(
                    expected=", ".join(sorted(valid_resize_to))
                )
            )

        # conflictive_join.fps
        fps = conflictive_join["fps"]
        valid_fps = {f.value for f in TargetFPS}
        if fps not in valid_fps:
            errors.append(
                locales.ConfigValidation["invalid_fps"].format(
                    expected=", ".join(sorted(valid_fps))
                )
            )

        # conflictive_join.channels
        channels = conflictive_join["channels"]
        valid_channels = {c.value for c in Channels}
        if channels not in valid_channels:
            errors.append(
                locales.ConfigValidation["invalid_channels"].format(
                    expected=", ".join(sorted(valid_channels))
                )
            )

        # app.language
        language = app["language"]
        valid_languages = {l.value for l in Language}
        if language not in valid_languages:
            errors.append(
                locales.ConfigValidation["invalid_language"].format(
                    expected=", ".join(sorted(valid_languages))
                )
            )

        if errors:
            raise InvalidConfigError(message="; ".join(errors))