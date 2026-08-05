import subprocess
from json import JSONDecodeError
from pathlib import Path

from pymedia.domain.media_input import MediaInput
from pymedia.ffmpeg.gif_cmd import gif_cmd
from pymedia.logger import get_logger

logger = get_logger("gif")


def gif_command(
    path: Path,
    fps: int | None = None,
    scale: int | None = None,
    start_point: str | None = None,
    end_point: str | None = None,
    crop: str | None = None,
    gyrate: int | None = None,
    output_name: str | None = None,
) -> None:

    try:
        media: MediaInput = MediaInput.load(path)
    except (ValueError, subprocess.CalledProcessError, JSONDecodeError, OSError):
        logger.error(f"Probe indica formato inválido: {path}")
        exit()

    cmd = gif_cmd(
        path, media, fps, scale, start_point, end_point, crop, gyrate, output_name
    )

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"Gif generado correctamente: {media.path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al generar el gif: {media.path}: {e.stderr}")
