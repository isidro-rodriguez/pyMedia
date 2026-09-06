"""Ejecución de ffprobe para obtener los metadatos de un medio."""

import json
import subprocess
from pathlib import Path

from pymedia.data.subtitle_formats import SUBTITLE_FORMATS
from pymedia.errors import FfprobeError
from pymedia.locales import _  # noqa
from pymedia.logger import Logger


def get_media_metadata(path: Path, logger: Logger) -> dict:
    """Obtiene metadatos del medio a procesar.

    Args:
        path: Ruta del fichero de vídeo a procesar.
        logger: Servicio de registro de mensajes.

    Returns:
        Metadatos del vídeo a procesar o errores si no es un vídeo válido.
    """
    try:
        cmd = [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(path),
        ]
        result = subprocess.run(
            args=cmd,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="strict",
        )
    except subprocess.CalledProcessError as err:
        raise FfprobeError(
            msg=_("ffprobe couldn't read %(path)s: %(err.stderr)s")
            % {"path": path, "err.stderr": err.stderr}
        ) from err

    data = json.loads(result.stdout)
    logger.debug(msg=_("ffprobe media data: %(data)s"), data=data)

    return data


def validate_subtitles_file_codec(subtitles_input: Path, logger: Logger) -> str:
    """Verifica que el archivo de subtítulos externo sea realmente subtítulos.

    Args:
        subtitles_input: Ruta del archivo de subtítulos a verificar.
        logger: Servicio de registro de mensajes.

    Raises:
        FfprobeError: Si ffprobe no puede leer el archivo, no detecta un
            formato de subtítulos conocido, o el formato detectado no es
            compatible con la extensión del archivo.
    """
    try:
        cmd = [
            "ffprobe",
            "-print_format",
            "json",
            "-show_format",
            str(subtitles_input),
        ]
        result = subprocess.run(
            args=cmd,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="strict",
        )
    except subprocess.CalledProcessError as err:
        raise FfprobeError(
            msg=_("ffprobe couldn't read %(path)s: %(err.stderr)s")
            % {"path": subtitles_input, "err.stderr": err.stderr}
        ) from err

    data = json.loads(result.stdout)
    logger.debug(msg=_("ffprobe subtitle file data: %(data)s"), data=data)

    format_name = data.get("format", {}).get("format_name", "")
    detected_codecs: set[str] = {
        token.strip() for token in format_name.split(",") if token.strip()
    }
    codec_name = next(
        (c for c in detected_codecs if c in SUBTITLE_FORMATS),
        None,
    )
    if codec_name is None:
        raise FfprobeError(
            msg=_(
                '"%(path)s" is not a recognized subtitle file '
                "(detected format: %(format_name)s)."
            )
            % {"path": subtitles_input, "format_name": format_name or "unknown"}
        )

    fmt = SUBTITLE_FORMATS.get(codec_name)
    if fmt is None or subtitles_input.suffix.lower() not in fmt.containers:
        raise FfprobeError(
            msg=_("%(path.suffix)s extension doesn't support %(codec_name)s subtitles.")
            % {"path.suffix": subtitles_input.suffix, "codec_name": codec_name}
        )
    return codec_name
