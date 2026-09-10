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
from pymedia.types import AudioCodecMode, PresetsTranscodeMode, VideoCodecMode


@dataclass(frozen=True, kw_only=True, slots=True)
class Transcode:
    """Parámetros de transcodificación que se usarán en ffmpeg.

    Attributes:
        video_codec: Códec de vídeo a utilizar en transcodificación.
        video_preset: Relación entre la velocidad de codificación
                y la calidad de compresión.
        video_crf: Parámetro de control de calidad para la codificación de vídeo.
        audio_codec: Códec de audio a utilizar en transcodificación.
        audio_bit_rate: Define la cantidad de datos digitales que se procesan por
                segundo.
    """

    video_codec: str
    video_preset: str
    video_crf: int
    audio_codec: str
    audio_bit_rate: str


@dataclass(frozen=True, kw_only=True, slots=True)
class TranscodePreset:
    """Perfiles de transcodificación declarados en `config.toml`.

    Attributes:
        fast: Perfil rápido, prioriza la velocidad de codificación.
        even: Perfil equilibrado entre velocidad y calidad.
        slow: Perfil de máxima calidad de compresión.
    """

    fast: Transcode
    even: Transcode
    slow: Transcode


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
    """Configuración de la aplicación cargada desde `config.toml`.

    Attributes:
        transcode: Perfiles de transcodificación que se usarán en ffmpeg.
        default_containers: Contenedores por defecto según tipo de fichero.
        app: Opciones de configuración de la aplicación.
    """

    transcode: TranscodePreset
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
            transcode=TranscodePreset(
                **{
                    preset: Transcode(**params)
                    for preset, params in data["transcode"].items()
                }
            ),
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

        transcode = data["transcode"]
        default_containers = data["default_containers"]
        app = data["app"]

        # El conjunto de perfiles debe coincidir con el declarado en la aplicación.
        valid_presets = {preset.value for preset in PresetsTranscodeMode}
        presets = transcode if isinstance(transcode, dict) else {}
        missing_presets = valid_presets - set(presets)
        unknown_presets = set(presets) - valid_presets
        if missing_presets or unknown_presets:
            errors.append(
                "\n"
                + _(
                    "Invalid configuration setting: transcode presets are expected "
                    "one of: %(expected)s."
                )
                % {"expected": ", ".join(sorted(valid_presets))}
            )

        # Los codecs de todos los perfiles condicionan los contenedores comunes.
        video_codecs: set[str] = set()
        audio_codecs: set[str] = set()
        media_pairs: list[tuple[str, str]] = []

        for preset_name, preset in presets.items():
            if not isinstance(preset, dict):
                errors.append(
                    "\n"
                    + _(
                        "Invalid configuration setting: transcode.%(preset)s is "
                        "expected to be a table of encoding parameters."
                    )
                    % {"preset": preset_name}
                )
                continue
            if preset_name not in valid_presets:
                continue  # ya reportado, evita validar claves ajenas

            # transcode.<preset>.video_codec
            video_codec = preset["video_codec"]
            valid_video_codecs = {v.value for v in VideoCodecMode}
            if video_codec not in valid_video_codecs:
                errors.append(
                    "\n"
                    + _(
                        "Invalid configuration setting: transcode.%(preset)s."
                        "video_codec is expected one of: %(expected)s."
                    )
                    % {
                        "preset": preset_name,
                        "expected": ", ".join(sorted(valid_video_codecs)),
                    }
                )

            # transcode.<preset>.video_preset
            video_preset = preset["video_preset"]
            if video_codec in VIDEO_CODECS:
                codec_presets = VIDEO_CODECS[video_codec].presets
                if codec_presets is not None and video_preset not in codec_presets:
                    errors.append(
                        "\n"
                        + _(
                            "Invalid configuration setting: transcode.%(preset)s."
                            "video_preset is expected one of: %(expected)s."
                        )
                        % {
                            "preset": preset_name,
                            "expected": ", ".join(codec_presets),
                        }
                    )

            # transcode.<preset>.video_crf
            video_crf = preset["video_crf"]
            if video_codec in VIDEO_CODECS:
                crf = VIDEO_CODECS[video_codec].crf
                if crf is not None and (
                    not isinstance(video_crf, int) or not crf[0] <= video_crf <= crf[1]
                ):
                    errors.append(
                        "\n"
                        + _(
                            "Invalid configuration setting: transcode.%(preset)s."
                            "video_crf is expected between %(min)s and %(max)s."
                        )
                        % {"preset": preset_name, "min": crf[0], "max": crf[1]}
                    )

            # transcode.<preset>.audio_codec
            audio_codec = preset["audio_codec"]
            valid_audio_codecs = {a.value for a in AudioCodecMode}
            if audio_codec not in valid_audio_codecs:
                errors.append(
                    "\n"
                    + _(
                        "Invalid configuration setting: transcode.%(preset)s."
                        "audio_codec is expected one of: %(expected)s."
                    )
                    % {
                        "preset": preset_name,
                        "expected": ", ".join(sorted(valid_audio_codecs)),
                    }
                )

            # transcode.<preset>.audio_bit_rate
            audio_bit_rate = preset["audio_bit_rate"]
            if audio_codec in AUDIO_CODECS:
                bit_rates = AUDIO_CODECS[audio_codec].bit_rates
                if bit_rates is not None and audio_bit_rate not in bit_rates:
                    errors.append(
                        "\n"
                        + _(
                            "Invalid configuration setting: transcode.%(preset)s."
                            "audio_bit_rate is expected one of: %(expected)s."
                        )
                        % {"preset": preset_name, "expected": ", ".join(bit_rates)}
                    )

            if video_codec in VIDEO_CODECS and audio_codec in AUDIO_CODECS:
                video_codecs.add(video_codec)
                audio_codecs.add(audio_codec)
                media_pairs.append((video_codec, audio_codec))

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
        if audio_codecs:
            supported_audio_containers = set.intersection(
                *(set(AUDIO_CODECS[codec].containers) for codec in audio_codecs)
            )
            if audio_container not in supported_audio_containers:
                errors.append(
                    "\n"
                    + _(
                        "Invalid configuration setting: default_container.audio is "
                        "expected one of: %(expected)s."
                    )
                    % {"expected": ", ".join(sorted(supported_audio_containers))}
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
        if media_pairs:
            common_containers = set.intersection(
                *(
                    set(VIDEO_CODECS[video].containers)
                    & set(AUDIO_CODECS[audio].containers)
                    for video, audio in media_pairs
                )
            )
            if media_container not in common_containers:
                errors.append(
                    "\n"
                    + _(
                        "Invalid configuration setting: default_container.media is "
                        "expected one of: %(expected)s."
                    )
                    % {"expected": ", ".join(sorted(common_containers))}
                )

        # default_container.subtitles
        subtitles_container = default_containers["subtitles"]
        if subtitles_container not in SUPPORTED.SUBTITLES:
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
        if stall_timeout is not None and (
            not isinstance(stall_timeout, int) or not 30 <= stall_timeout <= 600
        ):
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
