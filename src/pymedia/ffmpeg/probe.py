import json
import subprocess
from pathlib import Path


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
    return json.loads(result.stdout)
