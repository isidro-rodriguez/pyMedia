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
    logger.debug(msg=_("ffprobe data: %(data)s"), data=data)

    return data


def validate_subtitle_codec(path: Path, logger: Logger) -> str:
    """Verifica que el códec real del archivo coincide con su extensión.

    Args:
        path: Ruta del archivo de subtítulos a verificar.
        logger: Servicio de registro de mensajes.

    Raises:
        ValueError: Si ffprobe no detecta ningún stream de subtítulos, o si
            el códec detectado no es compatible con la extensión del archivo.
    """
    try:
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "s",
            "-show_entries",
            "stream=codec_name",
            "-of",
            "csv=p=0",
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
    logger.debug(msg=_("ffprobe data: %(data)s"), data=data)

    codec_name = result.stdout.strip()
    if not codec_name:
        raise FfprobeError(
            msg=_("ffprobe couldn't detect any subtitle stream in %(path)s")
            % {"path": path}
        )

    fmt = SUBTITLE_FORMATS.get(codec_name)
    if fmt is None or path.suffix.lower() not in fmt.containers:
        raise FfprobeError(
            msg=_("%(path.suffix)s container doesn't support %(codec_name)s.")
            % {"path.suffix": path.suffix, "codec_name": codec_name}
        )
    return codec_name
