import json
import subprocess
from pathlib import Path

from pymedia.logger import Logger


def probe(path: Path, logger: Logger) -> dict:
    """
    Obtiene metadatos del vídeo a procesar.

    Args:
        path: Ruta del fichero del que se va a sacar metadatos.
        logger: Servicio de registro de mensajes.

    Returns:
        Metadatos del vídeo a procesar o errores si no es un vídeo válido.
    """

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

    result = subprocess.run(args=cmd, capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    logger.debug(key="ffprobe_data", data=data)

    return data
