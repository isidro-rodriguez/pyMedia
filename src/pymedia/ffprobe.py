"""Ejecución de ffprobe para obtener los metadatos de un medio."""

import json
import subprocess
from pathlib import Path
from typing import Any

from pymedia.data.audio_codecs import AUDIO_CODECS
from pymedia.data.subtitles_formats import SUBTITLES_FORMATS
from pymedia.errors import FfprobeError
from pymedia.locales import _  # noqa
from pymedia.logger import Logger


def _run_ffprobe(args: list[str], path: Path) -> dict[str, Any]:
    """Ejecuta ffprobe y devuelve su JSON, con un error breve si falla.

    Args:
        args: Argumentos adicionales para ffprobe.
        path: Ruta del fichero a analizar.

    Raises:
        FfprobeError: Si ffprobe no está instalado o no puede leer el fichero.

    Returns:
        Diccionario con la salida JSON de ffprobe.
    """
    cmd = ["ffprobe", "-v", "error", "-print_format", "json", *args, str(path)]
    try:
        result = subprocess.run(
            args=cmd,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError as err:
        raise FfprobeError(msg=_("ffprobe was not found. Install ffmpeg.")) from err
    except subprocess.CalledProcessError as err:
        lines = [line for line in err.stderr.splitlines() if line.strip()]
        reason = lines[-1] if lines else str(err.returncode)
        raise FfprobeError(
            msg=_("ffprobe couldn't read %(path)s: %(err.stderr)s")
            % {"path": path, "err.stderr": reason}
        ) from err
    data: dict[str, Any] = json.loads(result.stdout)
    return data


def get_audio_codec(audio_input: Path, logger: Logger) -> str:
    """Verifica que el archivo de audio externo sea realmente audio.

    Args:
        audio_input: Ruta del archivo de audio a verificar.
        logger: Servicio de registro de mensajes.

    Raises:
        FfprobeError: Si ffprobe no puede leer el archivo, no detecta un
            formato de audio conocido, o el formato detectado no es
            compatible con la extensión del archivo.

    Returns:
        Nombre del códec de audio detectado y validado.
    """
    data = _run_ffprobe(
        ["-show_format", "-show_streams", "-select_streams", "a:0"], audio_input
    )
    logger.debug(msg=_("ffprobe audio file data: %(data)s"), data=data)

    streams = data.get("streams", [])
    codec_name: str | None = streams[0].get("codec_name") if streams else None
    if codec_name not in AUDIO_CODECS:
        format_name = data.get("format", {}).get("format_name", "")
        detected_codecs: set[str] = {
            token.strip() for token in format_name.split(",") if token.strip()
        }
        codec_name = next(
            (c for c in detected_codecs if c in AUDIO_CODECS),
            None,
        )
    if codec_name is None:
        raise FfprobeError(
            msg=_(
                '"%(path)s" is not a recognized audio file '
                "(detected format: %(format_name)s)."
            )
            % {
                "path": audio_input,
                "format_name": data.get("format", {}).get("format_name", "unknown"),
            }
        )

    fmt = AUDIO_CODECS.get(codec_name)
    if fmt is None or audio_input.suffix.lower() not in fmt.containers:
        raise FfprobeError(
            msg=_("%(path.suffix)s extension doesn't support %(codec_name)s audio.")
            % {"path.suffix": audio_input.suffix, "codec_name": codec_name}
        )
    return codec_name


def get_media_metadata(path: Path, logger: Logger) -> dict[str, Any]:
    """Obtiene metadatos del medio a procesar.

    Args:
        path: Ruta del fichero de vídeo a procesar.
        logger: Servicio de registro de mensajes.

    Returns:
        Metadatos del vídeo a procesar.

    Raises:
        FfprobeError: Si ffprobe no puede leer el fichero indicado.
    """
    data = _run_ffprobe(["-show_format", "-show_streams"], path)
    logger.debug(msg=_("ffprobe media data: %(data)s"), data=data)

    return data


def validate_subtitles_file_codec(subtitles_input: Path, logger: Logger) -> None:
    """Verifica que el archivo de subtítulos externo sea realmente subtítulos.

    Args:
        subtitles_input: Ruta del archivo de subtítulos a verificar.
        logger: Servicio de registro de mensajes.

    Raises:
        FfprobeError: Si ffprobe no puede leer el archivo, no detecta un
            formato de subtítulos conocido, o el formato detectado no es
            compatible con la extensión del archivo.

    Returns:
        Nombre del códec de subtítulos detectado y validado.
    """
    data = _run_ffprobe(["-show_format"], subtitles_input)
    logger.debug(msg=_("ffprobe subtitles file data: %(data)s"), data=data)

    format_name = data.get("format", {}).get("format_name", "")
    detected_codecs: set[str] = {
        token.strip() for token in format_name.split(",") if token.strip()
    }
    codec_name = next(
        (c for c in detected_codecs if c in SUBTITLES_FORMATS),
        None,
    )
    if codec_name is None:
        raise FfprobeError(
            msg=_(
                '"%(path)s" is not a recognized subtitles file '
                "(detected format: %(format_name)s)."
            )
            % {"path": subtitles_input, "format_name": format_name or "unknown"}
        )

    fmt = SUBTITLES_FORMATS.get(codec_name)
    if fmt is None or subtitles_input.suffix.lower() not in fmt.containers:
        raise FfprobeError(
            msg=_("%(path.suffix)s extension doesn't support %(codec_name)s subtitles.")
            % {"path.suffix": subtitles_input.suffix, "codec_name": codec_name}
        )
