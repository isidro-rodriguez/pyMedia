import subprocess
from json import JSONDecodeError
from pathlib import Path

from pymedia.domain.config import Config
from pymedia.domain.media_input import MediaInput, load
from pymedia.domain.transcoding_pipeline import TranscodingPipeline
from pymedia.ffmpeg.transcode_cmd import transcode_cmd


def transcode(
    path: list[Path], config: Config, transcoding_pipeline: TranscodingPipeline
) -> None:

    for p in path:
        try:
            media: MediaInput = load(p)
        except (ValueError, subprocess.CalledProcessError, JSONDecodeError, OSError):
            print(f"Formato inválido: {p}")
            continue

        try:
            transcoding_pipeline.validate(media)
        except ValueError:
            print(f"Formato inválido: {p}")
            continue

        cmd = transcode_cmd(p, config, transcoding_pipeline)
        if cmd is None:
            print(f"Parámetros inválidos: {p}")
            continue

        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error al transcodificar {p}: {e.stderr}")
