import subprocess
import tempfile
from datetime import timedelta
from json import JSONDecodeError
from pathlib import Path

from pymedia.commands.encode_command import transcode
from pymedia.models.errors import InvalidTrimPointsError
from pymedia.models.media import Media
from pymedia.models.pipeline import Pipeline
from pymedia.ffmpeg.split_cmd import split_cmd
from pymedia.logger import get_logger
from pymedia.utils import parse_trim_points

logger = get_logger("split")


def _split(path: Path, trim_points: list[timedelta], output_name: str | None) -> None:
    """Divide un vídeo en los puntos de corte indicados."""
    cmd = split_cmd(path, trim_points, output_name)
    if cmd is None:
        logger.error(f"Parámetros inválidos para división de vídeo: {path}")
        exit(1)
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"Vídeo dividido correctamente: {path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al dividir {path}: {e.stderr}")
        exit(1)


# TODO: opción de corte recodificado en el punto de corte exacto.
def split_command(
    path: Path,
    trim_points: str,
    encode_pipeline: Pipeline,
    output_name: str | None = None,
) -> None:

    try:
        media: Media = Media.load(path)
    except (ValueError, subprocess.CalledProcessError, JSONDecodeError, OSError):
        logger.error(f"Probe indica formato inválido: {path}")
        exit(1)

    if media.duration is None:
        logger.error(f"Probe no devolvió duración: {path}")
        exit(1)

    try:
        parsed_trim_points = parse_trim_points(trim_points)
    except InvalidTrimPointsError as e:
        logger.error(f"Los puntos de corte no pasan la verificación: {path} ({e})")
        exit(1)

    if parsed_trim_points is None:
        logger.error(f"Los puntos de corte no pasan la verificación: {path}")
        exit(1)

    md = media.duration.total_seconds()
    for p in parsed_trim_points:
        pc = p.total_seconds()
        if pc > md:
            logger.error(
                f"Punto de corte inválido: {pc} mayor a la duración del vídeo {md}"
            )
            exit(1)

    if encode_pipeline.has_operations:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir) / (path.stem + "_tmp" + path.suffix)
            if not transcode(media, encode_pipeline, output_name=str(tmp_path)):
                exit(1)
            _split(tmp_path, parsed_trim_points, output_name)
    else:
        _split(path, parsed_trim_points, output_name)
