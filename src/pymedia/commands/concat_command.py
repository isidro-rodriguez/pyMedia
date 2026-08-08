import subprocess
import tempfile
from json import JSONDecodeError
from pathlib import Path

from pymedia.ffmpeg.concat_demux_cmd import concat_demux_cmd
from pymedia.ffmpeg.concat_filter_cmd import concat_filter_cmd
from pymedia.logger import get_logger
from pymedia.models.media import Media
from pymedia.models.video_pipeline import VideoPipeline

logger = get_logger("concat")

# Timeout en segundos para la ejecución de ffmpeg (30 minutos)
FFMPEG_TIMEOUT = 1800


def _compatible_videos(media_inputs: list[Media]) -> bool:
    reference = media_inputs[0].concat_signature
    return all(m.concat_signature == reference for m in media_inputs[1:])


def concat_command(
    paths: list[Path],
    pipeline: VideoPipeline,
    output_name: str | None,
):

    media_inputs: list[Media] = []

    if output_name is None:
        output_name = paths[0].stem + "_concat" + paths[0].suffix

    for p in paths:
        try:
            media: Media = Media.load(p)
        except (
            ValueError,
            subprocess.CalledProcessError,
            JSONDecodeError,
            OSError,
        ):
            logger.error(f"Probe indica formato inválido: {p}")
            exit(1)
        media_inputs.append(media)

    # Verificar que no se mezclen vídeos con y sin audio
    has_audio = [m.audio is not None for m in media_inputs]
    if any(has_audio) and not all(has_audio):
        logger.error("No se puede unir: mezcla de vídeos con y sin audio.")
        exit(1)

    # Comprobar compatibilidad entre los vídeos a unir
    # Si son compatibles y no hay operaciones, se usa concat demuxer (copia directa)
    if _compatible_videos(media_inputs) and not pipeline.has_operations:
        with tempfile.TemporaryDirectory() as tmp_dir:
            list_txt = Path(tmp_dir) / "list.txt"
            with open(list_txt, "w", encoding="utf-8") as f:
                for p in paths:
                    f.write(f"file '{p.resolve().as_posix()}'\n")

            cmd = concat_demux_cmd(list_txt, Path(output_name))
            _run_ffmpeg(cmd, output_name)

    # Si no son compatibles o hay operaciones, se usa concat filter (recodificación)
    else:
        for m in media_inputs:
            pipeline.validate(m)

        cmd = concat_filter_cmd(media_inputs, pipeline, output_name)
        _run_ffmpeg(cmd, output_name)


def _run_ffmpeg(cmd: list[str], output_name: str) -> None:
    """Ejecuta ffmpeg con timeout y manejo de errores."""
    try:
        subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=FFMPEG_TIMEOUT,
        )
        logger.info(f"Vídeos unidos correctamente: {output_name}")
    except subprocess.TimeoutExpired:
        logger.error(
            f"Tiempo de espera agotado ({FFMPEG_TIMEOUT}s) al unir {output_name}."
        )
        exit(1)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al unir {output_name}: {e.stderr}")
        exit(1)
