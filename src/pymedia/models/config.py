"""Modelo de configuración de la aplicación y su validación."""

import tomllib
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path

import platformdirs

from pymedia.data.audio_codecs import AUDIO_CODECS
from pymedia.data.supported import SUPPORTED
from pymedia.data.video_codecs import VIDEO_CODECS
from pymedia.errors import ConfigError
from pymedia.locales import _  # noqa
from pymedia.types import AudioCodecMode, VideoCodecMode


@dataclass(frozen=True, kw_only=True, slots=True)
class Encode:
    """Parámetros de transcodificación que se usarán en ffmpeg.

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
class DefaultContainers:
    """Contenedores por defecto según el tipo fichero multimedia.

    Attributes:
        animated_image: Contenedor por defecto de imágenes animadas.
        audio_track: Contenedor por defecto de pistas de audio.
        image: Contenedor por defecto de imágenes.
        media: Contenedor por defecto de vídeos con audios y subtítulos.
        subtitles: Contenedor por defecto de subtítulos.
    """

    animated_image: str
    audio_track: str
    image: str
    media: str
    subtitles: str


@dataclass(frozen=True, kw_only=True, slots=True)
class App:
    """Opciones de configuración de la aplicación.

    Attributes:
        language: Lenguaje de la aplicación.
        stall_timeout: Retardo, en segundos, para matar el proceso ante bloqueo.
    """

    language: str
    stall_timeout: int


@dataclass(frozen=True, kw_only=True, slots=True)
class Config:
    """Actuaciones ante valores conflictivos en CONCAT filter.

    Attributes:
        encode: Parámetros de transcodificación que se usarán en ffmpeg.
        app: Opciones de configuración de la aplicación.
    """

    encode: Encode
    default_containers: DefaultContainers
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
            ConfigError: Si `config.toml` presenta parámetros no válidos.
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
            default_containers=DefaultContainers(**data["default_containers"]),
            app=App(**data["app"]),
        )

    @staticmethod
    def _create(path: Path) -> None:
        """Copia el config por defecto desde los recursos a la ruta de usuario."""
        path.parent.mkdir(parents=True, exist_ok=True)
        src = (
            files("pymedia.resources")
            .joinpath("config.toml")
            .read_text(encoding="utf-8")
        )
        path.write_text(src, encoding="utf-8")

    # =========================================================================
    #  Validación de config.toml
    # =========================================================================

    @staticmethod
    def _validate(data: dict) -> None:
        """Valida los valores del config.toml."""
        errors: list[str] = []

        encode = data["encode"]
        default_containers = data["default_containers"]
        app = data["app"]

        # encode.video_codec
        video_codec = encode["video_codec"]
        valid_video_codecs = {v.value for v in VideoCodecMode}
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
        valid_audio_codecs = {a.value for a in AudioCodecMode}
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

        # default_container.animated_image
        animated_image_container = default_containers["animated_image"]
        if animated_image_container not in SUPPORTED.ANIMATED:
            errors.append(
                "\n"
                + _(
                    "Invalid configuration setting: default_container.animated_image "
                    "is expected one of: %(expected)s."
                )
                % {"expected": ", ".join(SUPPORTED.ANIMATED)}
            )

        # default_container.audio
        audio_container = default_containers["audio_track"]
        if audio_codec in AUDIO_CODECS:
            supported_audio_containers = AUDIO_CODECS[audio_codec].containers
            if audio_container not in supported_audio_containers:
                errors.append(
                    "\n"
                    + _(
                        "Invalid configuration setting: default_container.audio is "
                        "expected one of: %(expected)s."
                    )
                    % {"expected": ", ".join(set(supported_audio_containers))}
                )

        # default_container.image
        image_container = default_containers["image"]
        if image_container not in SUPPORTED.IMAGES:
            errors.append(
                "\n"
                + _(
                    "Invalid configuration setting: default_container.image "
                    "is expected one of: %(expected)s."
                )
                % {"expected": ", ".join(SUPPORTED.IMAGES)}
            )

        # default_container.media
        media_container = default_containers["media"]
        if video_codec in VIDEO_CODECS and audio_codec in AUDIO_CODECS:
            video_containers = VIDEO_CODECS[video_codec].containers
            audio_containers = AUDIO_CODECS[audio_codec].containers
            if (
                media_container not in video_containers
                or media_container not in audio_containers
            ):
                common = sorted(set(video_containers) & set(audio_containers))
                errors.append(
                    "\n"
                    + _(
                        "Invalid configuration setting: default_container.media is "
                        "expected one of: %(expected)s."
                    )
                    % {"expected": ", ".join(common)}
                )

        # default_container.subtitles
        subtitle_container = default_containers["subtitles"]
        if subtitle_container not in SUPPORTED.SUBTITLES:
            errors.append(
                "\n"
                + _(
                    "Invalid configuration setting: default_container.subtitles "
                    "is expected one of: %(expected)s."
                )
                % {"expected": ", ".join(SUPPORTED.SUBTITLES)}
            )

        # app.language
        language = app["language"]
        if language not in SUPPORTED.LANGUAGES:
            errors.append(
                "\n"
                + _(
                    "Invalid configuration setting: app.language is expected one of: "
                    "%(expected)s."
                )
                % {"expected": ", ".join(SUPPORTED.LANGUAGES)}
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
            raise ConfigError(
                msg=_("Invalid configuration: %(msg)s") % {"msg": "; ".join(errors)}
            )
