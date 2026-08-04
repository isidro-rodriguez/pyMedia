import subprocess
import tempfile
from json import JSONDecodeError
from pathlib import Path

from pymedia.domain.encode_pipeline import EncodePipeline
from pymedia.domain.media_input import MediaInput
from pymedia.ffmpeg.concat_demux_cmd import concat_demux_cmd
from pymedia.logger import get_logger

logger = get_logger("concat")


def concat_command(
    paths: list[Path],
    pipeline: EncodePipeline,
    output_name: str | None,
):

    media_inputs: list[MediaInput] = []

    with tempfile.TemporaryDirectory() as tmp_dir:
        list_txt = Path(tmp_dir) / "list.txt"
        with open(list_txt, "w", encoding="utf-8") as f:
            for p in paths:
                try:
                    media: MediaInput = MediaInput.load(p)
                except (
                    ValueError,
                    subprocess.CalledProcessError,
                    JSONDecodeError,
                    OSError,
                ):
                    logger.error(f"Probe indica formato inválido: {p}")
                    exit(1)
                media_inputs.append(media)
                f.write(f"file '{p.resolve().as_posix()}'\n")

        if output_name is None:
            output_name = paths[0].stem + "_concat" + paths[0].suffix

        if not pipeline.has_operations:
            cmd = concat_demux_cmd(list_txt, Path(output_name))
        else:
            print("TODO")

        if cmd is None:
            logger.error("Parámetros inválidos para unión de vídeos.")
            exit(1)

        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Vídeos unidos correctamente: {output_name}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error al unir {output_name}: {e.stderr}")
            exit(1)
