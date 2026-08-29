import tomllib
from dataclasses import dataclass
from enum import Enum
from importlib.resources import files
from pathlib import Path

import platformdirs

from pymedia.data.audio_codecs import AUDIO_CODECS
from pymedia.data.video_codecs import VIDEO_CODECS
from pymedia.errors import InvalidConfigError
from pymedia.locales import _


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

    ENGLISH = "english"
    # FRENCH = "french"
    # GERMAN = "german"
    # ITALIAN = "italian"
    SPANISH = "spanish"
    SYSTEM = "system"


class Height(Enum):
    """Altura en que se redimensionan los vídeos en uniones conflictivas."""

    MAX_HEIGHT = "max_height"
    MIN_HEIGHT = "min_height"
    REJECT_INCREASE = "reject_increase"


class TargetFPS(Enum):
    """FPS en el que se transcodificarán los vídeos en uniones conflictivas."""

    MAX_FPS = "max_fps"
    MIN_FPS = "min_fps"


class VideoCodec(Enum):
    """Lista de códecs de vídeo modernos disponibles en esta aplicación."""

    AV1 = "av1"
    H264 = "h264"
    H265 = "h265"
    HEVC = "hevc"


@dataclass(frozen=True, kw_only=True, slots=True)
class Encode:
    """
    Parámetros de transcodificación que se usarán en ffmpeg.

    Attributes:
        video_codec: Códec de vídeo a utilizar en transcodificación.
        video_preset: Relación entre la velocidad de codificación
                y la calidad de compresión.
        video_crf: Parámetro de control de calidad para la codificación de vídeo.
        audio_codec: Códec de vídeo a utilizar en transcodificación.
        audio_bit_rate: Define cantidad datos digitales que se procesan por segundo
    """

    video_codec: str
    video_preset: str
    video_crf: int
    audio_codec: str
    audio_bit_rate: str


@dataclass(frozen=True, kw_only=True, slots=True)
class ConflictiveConcat:
    """
    Actuaciones ante valores conflictivos en CONCAT filter.

    Attributes:
        fps: Si transcodifica los vídeos al de menor FPS o el mayor.
        channels: Canales de salida de audio por defecto si los vídeos a
                concatenar tienes pistas de audio con canales incompatibles.
    """

    height: str
    fps: str
    channels: str


@dataclass(frozen=True, kw_only=True, slots=True)
class App:
    """
    Opciones de configuración de la aplicación.

    Attributes:
        language: Lenguaje de la aplicación.
        default_container: Formato que agrupa y sincroniza video, audio y subtítulos.
        stall_timeout: Retardo, en segundos, para matar el proceso ante bloqueo.
    """

    language: str
    default_container: str
    stall_timeout: int


@dataclass(frozen=True, kw_only=True, slots=True)
class Config:
    """
    Actuaciones ante valores conflictivos en CONCAT filter.

    Attributes:
        encode: Parámetros de transcodificación que se usarán en ffmpeg.
        conflictive_concat: Actuaciones ante valores conflictivos en CONCAT filter.
        app: Opciones de configuración de la aplicación.
    """

    encode: Encode
    conflictive_concat: ConflictiveConcat
    app: App

    @classmethod
    def load(cls) -> "Config":
        """Carga la configuración almacenada en el `config.toml` del usuario.

        Comprueba la existencia de todas las llaves y si estas son valores válidos.
        Si no existiese `config.toml` en el directorio de la aplicación, copia la
        configuración por defecto de `resources` al directorio del usuario.

        Returns:
            Configuración validada y cargada lista para consumo de la pyMedia.

        Raises:
            InvalidConfigError: Si `config.toml` presenta parámetros no válidos.
        """
        path = (
            Path(
                platformdirs.user_config_dir(
                    appname="pymedia", appauthor=False, roaming=True
                )
            )
            / "config.toml"
        )
        if not path.exists():
            cls._create(path)

        with path.open("rb") as f:
            data = tomllib.load(f)
            cls._validate(data)

        return cls(
            encode=Encode(**data["encode"]),
            conflictive_concat=ConflictiveConcat(**data["conflictive_concat"]),
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
        conflictive_concat = data["conflictive_concat"]
        app = data["app"]

        # encode.video_codec
        video_codec = encode["video_codec"]
        valid_video_codecs = {v.value for v in VideoCodec}
        if video_codec not in valid_video_codecs:
            errors.append(
                "\n"
                + _(
                    "Invalid configuration setting: encode.video_codec is expected "
                    "one of: %(expected)s."
                )
                % {"expected": ", ".join(sorted(valid_video_codecs))}
            )

        # encode.video_preset
        video_preset = encode["video_preset"]
        if video_codec in VIDEO_CODECS:
            presets = VIDEO_CODECS[video_codec].presets
            if presets is not None and video_preset not in presets:
                errors.append(
                    "\n"
                    + _(
                        "Invalid configuration setting: encode.video_preset is "
                        "expected one of: %(expected)s."
                    )
                    % {"expected": ", ".join(presets)}
                )

        # encode.video_crf
        video_crf = encode["video_crf"]
        if video_codec in VIDEO_CODECS:
            crf = VIDEO_CODECS[video_codec].crf
            if crf is not None and not crf[0] <= video_crf <= crf[1]:
                errors.append(
                    "\n"
                    + _(
                        "Invalid configuration setting: encode.video_crf is expected "
                        "between %(min)s and %(max)s."
                    )
                    % {"min": crf[0], "max": crf[1]}
                )

        # encode.audio_codec
        audio_codec = encode["audio_codec"]
        valid_audio_codecs = {a.value for a in AudioCodec}
        if audio_codec not in valid_audio_codecs:
            errors.append(
                "\n"
                + _(
                    "Invalid configuration setting: encode.audio_codec is expected "
                    "one of: %(expected)s."
                )
                % {"expected": ", ".join(sorted(valid_audio_codecs))}
            )

        # encode.audio_bit_rate
        audio_bit_rate = encode["audio_bit_rate"]
        if audio_codec in AUDIO_CODECS:
            bit_rates = AUDIO_CODECS[audio_codec].bit_rates
            if bit_rates is not None and audio_bit_rate not in bit_rates:
                errors.append(
                    "\n"
                    + _(
                        "Invalid configuration setting: encode.audio_bit_rate is "
                        "expected one of: %(expected)s."
                    )
                    % {"expected": ", ".join(bit_rates)}
                )

        # conflictive_concat.height
        height = conflictive_concat["height"]
        valid_height = {r.value for r in Height}
        if height not in valid_height:
            errors.append(
                "\n"
                + _(
                    "Invalid configuration setting: conflictive_concat.height is "
                    "expected one of: %(expected)s."
                )
                % {"expected": ", ".join(sorted(valid_height))}
            )

        # conflictive_concat.fps
        fps = conflictive_concat["fps"]
        valid_fps = {f.value for f in TargetFPS}
        if fps not in valid_fps:
            errors.append(
                "\n"
                + _(
                    "Invalid configuration setting: conflictive_concat.fps is "
                    "expected one of: %(expected)s."
                )
                % {"expected": ", ".join(sorted(valid_fps))}
            )

        # conflictive_concat.channels
        channels = conflictive_concat["channels"]
        valid_channels = {c.value for c in Channels}
        if channels not in valid_channels:
            errors.append(
                "\n"
                + _(
                    "Invalid configuration setting: conflictive_concat.channels is "
                    "expected one of: %(expected)s."
                )
                % {"expected": ", ".join(sorted(valid_channels))}
            )

        # app.language
        language = app["language"]
        valid_languages = {lang.value for lang in Language}
        if language not in valid_languages:
            errors.append(
                "\n"
                + _(
                    "Invalid configuration setting: app.language is expected one of: "
                    "%(expected)s."
                )
                % {"expected": ", ".join(sorted(valid_languages))}
            )

        # app.default_container
        default_container = app["default_container"]
        if video_codec in VIDEO_CODECS and audio_codec in AUDIO_CODECS:
            video_containers = VIDEO_CODECS[video_codec].containers
            audio_containers = AUDIO_CODECS[audio_codec].containers
            if (
                default_container not in video_containers
                or default_container not in audio_containers
            ):
                common = sorted(set(video_containers) & set(audio_containers))
                errors.append(
                    "\n"
                    + _(
                        "Invalid configuration setting: encode.default_container is "
                        "expected one of: %(expected)s."
                    )
                    % {"expected": ", ".join(common)}
                )

        # app.stall_timeout
        stall_timeout = app["stall_timeout"]
        if stall_timeout is not None and not 30 <= stall_timeout <= 600:
            errors.append(
                "\n"
                + _(
                    "Invalid configuration setting: app.stall_timeout is expected to "
                    "an integer between 30 to 600."
                )
            )

        if errors:
            raise InvalidConfigError(message="; ".join(errors))
