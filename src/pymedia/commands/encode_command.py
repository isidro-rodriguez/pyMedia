import subprocess
from json import JSONDecodeError
from pathlib import Path

from pymedia.domain.encode_pipeline import EncodePipeline
from pymedia.domain.errors import PipelineValidationError
from pymedia.domain.media_input import MediaInput
from pymedia.ffmpeg.encode_cmd import encode_cmd
from pymedia.logger import get_logger

logger = get_logger("encode")


def transcode(
    media: MediaInput,
    encode_pipeline: EncodePipeline,
    output_name: str | None = None,
) -> bool:
    """Transcodifica un único archivo. Devuelve True si tuvo éxito."""
    try:
        encode_pipeline.validate(media)
    except PipelineValidationError as e:
        logger.error(f"Formato no pasa verificación: {media.path} ({e})")
        return False
    except ValueError:
        logger.error(f"Formato no pasa verificación: {media.path}")
        return False

    if not encode_pipeline.has_operations:
        logger.warning(f"Sin operaciones aplicables, omitido: {media.path}")
        return False

    cmd = encode_cmd(media.path, media, encode_pipeline, output_name=output_name)
    if cmd is None:
        logger.error(f"Parámetros inválidos: {media.path}")
        return False

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"Transcodificado correctamente: {media.path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al transcodificar {media.path}: {e.stderr}")
        return False


def encode_command(
    paths: list[Path],
    encode_pipeline: EncodePipeline,
    output_name: str | None = None,
) -> None:

    for i, path in enumerate(paths):
        try:
            media: MediaInput = MediaInput.load(path)
        except (ValueError, subprocess.CalledProcessError, JSONDecodeError, OSError):
            logger.error(f"Probe indica formato inválido: {path}")
            continue

        if output_name is not None and len(paths) > 1:
            output = f"{Path(output_name).stem}_{i}{path.suffix}"
        else:
            output = output_name

        transcode(media, encode_pipeline, output)
