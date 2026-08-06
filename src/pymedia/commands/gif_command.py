import subprocess
from json import JSONDecodeError
from pathlib import Path

from pymedia.domain.encode_pipeline import EncodePipeline
from pymedia.domain.errors import PipelineValidationError
from pymedia.domain.media_input import MediaInput
from pymedia.ffmpeg.gif_cmd import gif_cmd
from pymedia.logger import get_logger

logger = get_logger("gif")


def gif_command(
    path: Path,
    pipeline: EncodePipeline,
    fps: int | None = None,
    start_point: str | None = None,
    end_point: str | None = None,
    output_name: str | None = None,
) -> None:

    try:
        media: MediaInput = MediaInput.load(path)
    except (ValueError, subprocess.CalledProcessError, JSONDecodeError, OSError):
        logger.error(f"Probe indica formato inválido: {path}")
        exit(1)

    try:
        pipeline.validate(media)
    except PipelineValidationError as e:
        logger.error(f"Formato no pasa verificación: {media.path} ({e})")
        exit(1)
    except ValueError:
        logger.error(f"Formato no pasa verificación: {media.path}")
        exit(1)

    cmd = gif_cmd(path, pipeline, media, fps, start_point, end_point, output_name)

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"Gif generado correctamente: {media.path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al generar el gif: {media.path}: {e.stderr}")
