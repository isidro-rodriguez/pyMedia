import json
import subprocess
from pathlib import Path

from pymedia.feedback.logger import get_logger, log_debug

logger = get_logger("probe")


def probe(path: Path) -> dict:
    """Ejecuta ffprobe y devuelve el JSON parseado."""
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
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    log_debug(logger, "ffprobe_data", data=data)
    return data
