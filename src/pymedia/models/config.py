"""Modelo de configuración de la aplicación y su validación."""

import tomllib
from collections.abc import Iterable
from dataclasses import dataclass, fields
from importlib.resources import files
from pathlib import Path
from typing import Any, cast

import platformdirs

from pymedia.data.audio_codecs import AUDIO_CODECS
from pymedia.data.language_codes import resolve_language
from pymedia.data.supported import SUPPORTED
from pymedia.data.video_codecs import VIDEO_CODECS
from pymedia.errors import ConfigError
from pymedia.locales import translate as _
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
            ConfigError: Si `config.toml` no es un TOML válido, le faltan o sobran
                claves, o presenta parámetros no válidos.
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

        data = _read_toml(path)
        _validate(data)

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


# =============================================================================
#  Lectura y validación de config.toml
# =============================================================================

_SECTIONS: dict[str, type[Any]] = {"app": App, "default_containers": DefaultContainers}
_STALL_TIMEOUT_RANGE = (30, 600)


def _read_toml(path: Path) -> dict[str, Any]:
    """Lee `config.toml`, traduciendo un TOML mal formado a `ConfigError`."""
    try:
        with path.open("rb") as f:
            return tomllib.load(f)
    except tomllib.TOMLDecodeError as err:
        raise ConfigError(
            msg=_("Configuration file is not valid TOML: %(path)s (%(reason)s)")
            % {"path": path, "reason": err}
        ) from err


def _validate(data: dict[str, Any]) -> None:
    """Valida el config.toml acumulando todos los errores de valor.

    Raises:
        ConfigError: Si falta o sobra alguna tabla o clave, o algún valor no es
            válido.
    """
    _validate_structure(data)
    errors, media_pairs = _validate_transcode(data["transcode"])
    errors += _validate_default_containers(data["default_containers"], media_pairs)
    errors += _validate_app(data["app"])
    _raise_if_errors(errors)


def _raise_if_errors(errors: list[str]) -> None:
    """Eleva `ConfigError` con todos los errores acumulados, si los hay."""
    if errors:
        raise ConfigError(
            msg=_("Invalid configuration: %(msg)s") % {"msg": "; ".join(errors)}
        )


# -----------------------------------------------------------------------------
#  Estructura: tablas y claves
# -----------------------------------------------------------------------------


def _validate_structure(data: dict[str, Any]) -> None:
    """Comprueba tablas y claves antes de validar valores, que las presuponen.

    Raises:
        ConfigError: Si falta o sobra alguna tabla o clave.
    """
    errors: list[str] = []
    for name, model in _SECTIONS.items():
        errors += _table_errors(data.get(name), name, model)
    errors += _transcode_structure_errors(data.get("transcode"))
    _raise_if_errors(errors)


def _table_errors(table: object, path: str, model: type[Any]) -> list[str]:
    """Compara las claves de una tabla con los campos de su modelo."""
    if not isinstance(table, dict):
        return [
            "\n"
            + _("Invalid configuration setting: %(setting)s is expected to be a table.")
            % {"setting": path}
        ]
    keys = set(cast(dict[str, Any], table))
    expected = {field.name for field in fields(model)}
    missing = [
        "\n"
        + _("Missing configuration setting: %(setting)s.")
        % {"setting": f"{path}.{key}"}
        for key in sorted(expected - keys)
    ]
    unknown = [
        "\n"
        + _("Unknown configuration setting: %(setting)s.")
        % {"setting": f"{path}.{key}"}
        for key in sorted(keys - expected)
    ]
    return missing + unknown


def _transcode_structure_errors(transcode: object) -> list[str]:
    """Comprueba que `[transcode]` declare justo los perfiles de la aplicación."""
    presets = cast(dict[str, Any], transcode) if isinstance(transcode, dict) else {}
    valid_presets = {preset.value for preset in PresetsTranscodeMode}
    errors: list[str] = []
    if set(presets) != valid_presets:
        errors.append(
            "\n"
            + _(
                "Invalid configuration setting: transcode presets are expected "
                "one of: %(expected)s."
            )
            % {"expected": ", ".join(sorted(valid_presets))}
        )
    for name, preset in presets.items():
        if not isinstance(preset, dict):
            errors.append(
                "\n"
                + _(
                    "Invalid configuration setting: transcode.%(preset)s is "
                    "expected to be a table of encoding parameters."
                )
                % {"preset": name}
            )
        elif name in valid_presets:
            errors += _table_errors(preset, f"transcode.{name}", Transcode)
    return errors


# -----------------------------------------------------------------------------
#  Valores
# -----------------------------------------------------------------------------


def _one_of_error(setting: str, expected: Iterable[str]) -> str:
    """Error de un ajuste que solo admite ciertos valores."""
    return "\n" + _(
        "Invalid configuration setting: %(setting)s is expected one of: %(expected)s."
    ) % {"setting": setting, "expected": ", ".join(expected)}


def _range_error(setting: str, low: int, high: int) -> str:
    """Error de un ajuste que admite un entero dentro de un rango."""
    return "\n" + _(
        "Invalid configuration setting: %(setting)s is expected to be an integer "
        "between %(min)s and %(max)s."
    ) % {"setting": setting, "min": low, "max": high}


def _is_int_between(value: object, low: int, high: int) -> bool:
    """Indica si `value` es un entero, no booleano, dentro de `[low, high]`."""
    return (
        isinstance(value, int) and not isinstance(value, bool) and low <= value <= high
    )


def _validate_transcode(
    presets: dict[str, Any],
) -> tuple[list[str], list[tuple[str, str]]]:
    """Valida los parámetros de cada perfil de transcodificación.

    Returns:
        Errores encontrados y pares `(códec vídeo, códec audio)` conocidos, que
        condicionan los contenedores por defecto.
    """
    errors: list[str] = []
    media_pairs: list[tuple[str, str]] = []
    for name, preset in presets.items():
        errors += _validate_video_preset(name, preset)
        errors += _validate_audio_preset(name, preset)
        video_codec, audio_codec = preset["video_codec"], preset["audio_codec"]
        if video_codec in VIDEO_CODECS and audio_codec in AUDIO_CODECS:
            media_pairs.append((video_codec, audio_codec))
    return errors, media_pairs


def _validate_video_preset(name: str, preset: dict[str, Any]) -> list[str]:
    """Valida códec, preset y CRF de vídeo de un perfil."""
    errors: list[str] = []
    codec = preset["video_codec"]
    valid_codecs = sorted(v.value for v in VideoCodecMode)
    if codec not in valid_codecs:
        errors.append(_one_of_error(f"transcode.{name}.video_codec", valid_codecs))
    if codec not in VIDEO_CODECS:
        return errors

    codec_presets = VIDEO_CODECS[codec].presets
    if codec_presets is not None and preset["video_preset"] not in codec_presets:
        errors.append(_one_of_error(f"transcode.{name}.video_preset", codec_presets))
    crf = VIDEO_CODECS[codec].crf
    if crf is not None and not _is_int_between(preset["video_crf"], *crf):
        errors.append(_range_error(f"transcode.{name}.video_crf", *crf))
    return errors


def _validate_audio_preset(name: str, preset: dict[str, Any]) -> list[str]:
    """Valida códec y tasa de bits de audio de un perfil."""
    errors: list[str] = []
    codec = preset["audio_codec"]
    valid_codecs = sorted(a.value for a in AudioCodecMode)
    if codec not in valid_codecs:
        errors.append(_one_of_error(f"transcode.{name}.audio_codec", valid_codecs))
    if codec not in AUDIO_CODECS:
        return errors

    bit_rates = AUDIO_CODECS[codec].bit_rates
    if bit_rates is not None and preset["audio_bit_rate"] not in bit_rates:
        errors.append(_one_of_error(f"transcode.{name}.audio_bit_rate", bit_rates))
    return errors


def _validate_default_containers(
    containers: dict[str, Any], media_pairs: list[tuple[str, str]]
) -> list[str]:
    """Valida los contenedores por defecto frente a los códecs de los perfiles."""
    errors: list[str] = []
    for key, supported in (
        ("animated_image", SUPPORTED.ANIMATED),
        ("image", SUPPORTED.IMAGES),
        ("subtitles", SUPPORTED.SUBTITLES),
    ):
        if containers[key] not in supported:
            errors.append(_one_of_error(f"default_containers.{key}", supported))

    # Los códecs de todos los perfiles condicionan los contenedores comunes.
    if not media_pairs:
        return errors
    audio = _common_containers(AUDIO_CODECS[a].containers for _v, a in media_pairs)
    if containers["audio_track"] not in audio:
        errors.append(_one_of_error("default_containers.audio_track", sorted(audio)))
    media = _common_containers(
        set(VIDEO_CODECS[v].containers) & set(AUDIO_CODECS[a].containers)
        for v, a in media_pairs
    )
    if containers["media"] not in media:
        errors.append(_one_of_error("default_containers.media", sorted(media)))
    return errors


def _common_containers(groups: Iterable[Iterable[str]]) -> set[str]:
    """Intersección de varios grupos de contenedores."""
    return set.intersection(*(set(group) for group in groups))


def _validate_app(app: dict[str, Any]) -> list[str]:
    """Valida idioma y tiempo de bloqueo de la aplicación."""
    errors: list[str] = []
    # Literal soportado o cualquier alias que resuelva a uno.
    language = app["language"]
    resolved = resolve_language(language) if isinstance(language, str) else None
    language_name = resolved.english.casefold() if resolved is not None else language
    if language_name not in SUPPORTED.LANGUAGES:
        errors.append(_one_of_error("app.language", SUPPORTED.LANGUAGES))
    if not _is_int_between(app["stall_timeout"], *_STALL_TIMEOUT_RANGE):
        errors.append(_range_error("app.stall_timeout", *_STALL_TIMEOUT_RANGE))
    return errors
