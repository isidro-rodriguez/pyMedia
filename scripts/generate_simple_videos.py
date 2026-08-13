#!/usr/bin/env python3
"""
Genera vídeos placeholder (480p/720p/1080p, sin audio, 10 s) para testear
transcodificación. Patrón de nombre: NOMBRE_CODEC_RESOLUCION. EXT
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import NamedTuple

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

DURATION = 10
FPS = 30
OUTPUT_DIR = Path("../.local/fixtures")

RESOLUTIONS = {
    "480p": "854x480",
    "720p": "1280x720",
    "1080p": "1920x1080",
}

# codec -> (encoder ffmpeg, extra args, extensión)
CODECS = {
    "h264": ("libx264", ["-preset", "ultrafast"], "mp4"),
    "h265": ("libx265", ["-preset", "ultrafast"], "mp4"),
    "av1": ("libsvtav1", ["-preset", "13"], "mp4"),
}


class VideoSpec(NamedTuple):
    nombre: str
    codec: str
    filtro_tpl: str  # admite {res} y {fps}


VIDEOS = [
    VideoSpec("cell", "h264", "cellauto=s={res}:rate={fps}"),
    VideoSpec("solid", "av1", "color=c=blue:s={res}:rate={fps}"),
    VideoSpec("mandrel", "h264", "mandelbrot=s={res}:rate={fps}"),
    VideoSpec("src", "h265", "testsrc=s={res}:rate={fps}"),
    VideoSpec("vsrc", "h265", "testsrc2=s={res}:rate={fps}"),
]


def generar_video(
    spec: VideoSpec, res_nombre: str, res_valor: str, destino: Path
) -> None:
    encoder, extra_args, ext = CODECS[spec.codec]
    filtro = spec.filtro_tpl.format(res=res_valor, fps=FPS)
    salida = destino / f"{spec.nombre}_{spec.codec}_{res_nombre}.{ext}"

    comando = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        filtro,
        "-t",
        str(DURATION),
        "-an",
        "-c:v",
        encoder,
        "-pix_fmt",
        "yuv420p",
        *extra_args,
        str(salida),
    ]
    try:
        subprocess.run(comando, check=True, capture_output=True, text=True)
        logger.info("Generado: %s", salida)
    except subprocess.CalledProcessError as exc:
        logger.error("Fallo al generar %s: %s", salida.name, exc.stderr.strip())


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    for spec in VIDEOS:
        for res_nombre, res_valor in RESOLUTIONS.items():
            generar_video(spec, res_nombre, res_valor, OUTPUT_DIR)


if __name__ == "__main__":
    main()
