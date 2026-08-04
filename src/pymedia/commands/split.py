import subprocess
from json import JSONDecodeError
from pathlib import Path

from pymedia.domain.config import Config
from pymedia.domain.encode_pipeline import EncodePipeline
from pymedia.domain.errors import PipelineValidationError
from pymedia.domain.media_input import MediaInput, load
from pymedia.ffmpeg.encode_cmd import encode_cmd
from pymedia.logger import get_logger

logger = get_logger("split")


def split_command(
    trim_points: str,
    paths: list[Path],
    config: Config,
    encode_pipeline: EncodePipeline,
    output_name: str | None = None,
) -> None:

    for p in paths:
        try:
            media: MediaInput = load(p)
        except (ValueError, subprocess.CalledProcessError, JSONDecodeError, OSError):
            logger.error(f"Probe indica formato inválido: {p}")
            continue

        try:
            encode_pipeline.validate(media)
        except PipelineValidationError as e:
            logger.error(f"Formato no pasa verificación: {p} ({e})")
            continue
        except ValueError:
            logger.error(f"Formato no pasa verificación: {p}")
            continue

        if not encode_pipeline.has_operations:
            logger.warning(f"Sin operaciones aplicables, omitido: {p}")
            continue

        cmd = encode_cmd(p, config, media, encode_pipeline, output_name=output_name)
        if cmd is None:
            logger.error(f"Parámetros inválidos: {p}")
            continue

        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Transcodificado correctamente: {p}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error al transcodificar {p}: {e.stderr}")
