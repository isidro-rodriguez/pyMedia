import subprocess
from json import JSONDecodeError
from pathlib import Path

from pymedia.domain.config import Config
from pymedia.domain.errors import PipelineValidationError
from pymedia.domain.media_input import MediaInput, load
from pymedia.domain.transcoding_pipeline import TranscodingPipeline
from pymedia.ffmpeg.transcode_cmd import transcode_cmd
from pymedia.logger import get_logger

logger = get_logger("transcode")


def transcode(
    paths: list[Path],
    config: Config,
    transcoding_pipeline: TranscodingPipeline,
    output_name: str | None = None,
) -> None:

    for p in paths:
        try:
            media: MediaInput = load(p)
        except (ValueError, subprocess.CalledProcessError, JSONDecodeError, OSError):
            logger.error(f"Probe indica formato inválido: {p}")
            continue

        try:
            transcoding_pipeline.validate(media)
        except PipelineValidationError as e:
            logger.error(f"Formato no pasa verificación: {p} ({e})")
            continue
        except ValueError:
            logger.error(f"Formato no pasa verificación: {p}")
            continue

        if not transcoding_pipeline.has_operations:
            logger.warning(f"Sin operaciones aplicables, omitido: {p}")
            continue

        cmd = transcode_cmd(
            p, config, media, transcoding_pipeline, output_name=output_name
        )
        if cmd is None:
            logger.error(f"Parámetros inválidos: {p}")
            continue

        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Error al transcodificar {p}: {e.stderr}")
