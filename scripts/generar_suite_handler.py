#!/usr/bin/env python3
"""Suite exhaustiva de vídeos de test para validar un handler de ffmpeg.

Nombre de archivo: NombreCorto_Codec_Resolucion_PatronTest.Ext
"""

from __future__ import annotations

import logging
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import NamedTuple

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

DURATION = 10
FPS = 30
OUTPUT_DIR = Path("../data/fixtures-advanced")

RES = {
    "480p": "854x480",
    "720p": "1280x720",
    "1080p": "1920x1080",
    "720pV": "720x1280",  # vertical, simula móvil
    "1080pV": "1080x1920",  # vertical, simula móvil
    "ultrawide": "2560x1080",
    "resimpar": "853x481",  # no divisible entre 2: fuerza padding/crop
}

ENCODER = {"h264": "libx264", "h265": "libx265", "av1": "libsvtav1"}

BuildCmd = Callable[[Path], list[str]]


def video_args(
    codec: str, pix_fmt: str = "yuv420p", extra: list[str] | None = None
) -> list[str]:
    return ["-c:v", ENCODER[codec], "-pix_fmt", pix_fmt] + (extra or [])


def fuente(nombre: str, res: str, extra: str = "") -> str:
    """Construye un filtro lavfi de tipo 'nombre=s=RES:rate=FPS[extra]'."""
    return f"{nombre}=s={res}:rate={FPS}{extra}"


def truncar_archivo(path: Path, fraccion: float = 0.6) -> None:
    """Corta el archivo tras generarlo, simulando una subida incompleta/corrupta."""
    datos = path.read_bytes()
    path.write_bytes(datos[: int(len(datos) * fraccion)])


class TestCase(NamedTuple):
    nombre_corto: str
    codec: str
    resolucion: str  # etiqueta para el nombre de archivo
    patron: str
    build_cmd: BuildCmd
    ext: str = "mp4"
    post_procesado: Callable[[Path], None] | None = None


# --- Builders de comando: uno por tipo de caso de prueba -------------------


def cmd_estandar(filtro: str, codec: str, pix_fmt: str = "yuv420p") -> BuildCmd:
    def build(salida: Path) -> list[str]:
        return [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            filtro,
            "-t",
            str(DURATION),
            "-an",
            *video_args(codec, pix_fmt),
            str(salida),
        ]

    return build


def cmd_rotacion(filtro: str, codec: str, grados: int) -> BuildCmd:
    def build(salida: Path) -> list[str]:
        return [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            filtro,
            "-t",
            str(DURATION),
            "-an",
            *video_args(codec),
            "-metadata:s:v:0",
            f"rotate={grados}",
            str(salida),
        ]

    return build


def cmd_sar(filtro: str, codec: str, sar: str) -> BuildCmd:
    def build(salida: Path) -> list[str]:
        return [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"{filtro},setsar={sar}",
            "-t",
            str(DURATION),
            "-an",
            *video_args(codec),
            str(salida),
        ]

    return build


def cmd_gop(filtro: str, codec: str, gop: int) -> BuildCmd:
    def build(salida: Path) -> list[str]:
        return [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            filtro,
            "-t",
            str(DURATION),
            "-an",
            *video_args(codec),
            "-g",
            str(gop),
            "-keyint_min",
            str(gop),
            str(salida),
        ]

    return build


def cmd_bframes(filtro: str, codec: str, bf: int) -> BuildCmd:
    def build(salida: Path) -> list[str]:
        return [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            filtro,
            "-t",
            str(DURATION),
            "-an",
            *video_args(codec),
            "-bf",
            str(bf),
            str(salida),
        ]

    return build


def cmd_hdr(filtro: str, codec: str) -> BuildCmd:
    def build(salida: Path) -> list[str]:
        return [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            filtro,
            "-t",
            str(DURATION),
            "-an",
            *video_args(codec, pix_fmt="yuv420p10le"),
            "-color_primaries",
            "bt2020",
            "-color_trc",
            "smpte2084",
            "-colorspace",
            "bt2020nc",
            str(salida),
        ]

    return build


def cmd_vfr(res_valor: str, codec: str) -> BuildCmd:
    """Concatena dos tramos con distinto framerate para forzar VFR real."""

    def build(salida: Path) -> list[str]:
        mitad = DURATION // 2
        filtro_complex = (
            f"testsrc=s={res_valor}:rate=15:d={mitad}[a];"
            f"testsrc=s={res_valor}:rate=30:d={mitad}[b];"
            f"[a][b]concat=n=2:v=1:a=0[v]"
        )
        return [
            "ffmpeg",
            "-y",
            "-filter_complex",
            filtro_complex,
            "-map",
            "[v]",
            "-an",
            "-fps_mode",
            "vfr",
            *video_args(codec),
            str(salida),
        ]

    return build


def cmd_multiaudio(filtro: str, codec: str) -> BuildCmd:
    def build(salida: Path) -> list[str]:
        return [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            filtro,
            "-f",
            "lavfi",
            "-i",
            f"sine=frequency=440:duration={DURATION}",
            "-f",
            "lavfi",
            "-i",
            f"sine=frequency=880:duration={DURATION}",
            "-t",
            str(DURATION),
            "-map",
            "0:v",
            "-map",
            "1:a",
            "-map",
            "2:a",
            *video_args(codec),
            "-c:a",
            "aac",
            "-metadata:s:a:0",
            "language=eng",
            "-metadata:s:a:1",
            "language=spa",
            str(salida),
        ]

    return build


RUIDO = f"color=c=black:s={{res}}:rate={FPS},noise=alls=60:allf=t+u"

# --- Suite de casos de prueba -----------------------------------------------

CASOS: list[TestCase] = [
    # Casos base: uno por familia de fuente lavfi disponible
    TestCase(
        "base",
        "h264",
        "720p",
        "estandar",
        cmd_estandar(fuente("testsrc", RES["720p"]), "h264"),
    ),
    TestCase(
        "base",
        "h265",
        "1080p",
        "estandar",
        cmd_estandar(fuente("testsrc2", RES["1080p"]), "h265"),
    ),
    TestCase(
        "base",
        "av1",
        "480p",
        "estandar",
        cmd_estandar(fuente("color", RES["480p"], ":c=blue"), "av1"),
    ),
    TestCase(
        "bars",
        "h264",
        "720p",
        "estandar",
        cmd_estandar(fuente("smptebars", RES["720p"]), "h264"),
    ),
    TestCase(
        "barshd",
        "h265",
        "1080p",
        "estandar",
        cmd_estandar(fuente("smptehdbars", RES["1080p"]), "h265"),
    ),
    TestCase(
        "grad",
        "h264",
        "480p",
        "estandar",
        cmd_estandar(fuente("gradients", RES["480p"]), "h264"),
    ),
    TestCase(
        "cell",
        "h264",
        "720p",
        "estandar",
        cmd_estandar(fuente("cellauto", RES["720p"]), "h264"),
    ),
    TestCase(
        "mandrel",
        "h265",
        "1080p",
        "estandar",
        cmd_estandar(fuente("mandelbrot", RES["1080p"]), "h265"),
    ),
    TestCase(
        "ruido",
        "h264",
        "480p",
        "estandar",
        cmd_estandar(RUIDO.format(res=RES["480p"]), "h264"),
    ),
    # Vertical / móvil
    TestCase(
        "vert",
        "h264",
        "720pV",
        "vertical",
        cmd_estandar(fuente("testsrc", RES["720pV"]), "h264"),
    ),
    TestCase(
        "vert",
        "h265",
        "1080pV",
        "vertical",
        cmd_estandar(fuente("testsrc2", RES["1080pV"]), "h265"),
    ),
    # Resolución / aspecto atípicos
    TestCase(
        "odd",
        "h264",
        "resimpar",
        "resolucionimpar",
        cmd_estandar(fuente("testsrc", RES["resimpar"]), "h264"),
    ),
    TestCase(
        "wide",
        "h264",
        "ultrawide",
        "aspectoinusual",
        cmd_estandar(fuente("gradients", RES["ultrawide"]), "h264"),
    ),
    TestCase(
        "sar",
        "h264",
        "720p",
        "saranamorfico",
        cmd_sar(fuente("testsrc", RES["720p"]), "h264", "4/3"),
    ),
    TestCase(
        "rot",
        "h264",
        "720p",
        "rotacion90",
        cmd_rotacion(fuente("testsrc2", RES["720p"]), "h264", 90),
    ),
    # Framerate
    TestCase("vfr", "h264", "720p", "frecuenciavariable", cmd_vfr(RES["720p"], "h264")),
    # GOP / estructura de frames
    TestCase(
        "gop",
        "h265",
        "1080p",
        "goplargo",
        cmd_gop(fuente("testsrc", RES["1080p"]), "h265", 300),
    ),
    TestCase(
        "gop",
        "h264",
        "480p",
        "gopcorto",
        cmd_gop(fuente("color", RES["480p"], ":c=blue"), "h264", 5),
    ),
    TestCase(
        "intra",
        "h264",
        "720p",
        "todointra",
        cmd_gop(fuente("testsrc2", RES["720p"]), "h264", 1),
    ),
    TestCase(
        "nobf",
        "h264",
        "720p",
        "sinbframes",
        cmd_bframes(fuente("testsrc", RES["720p"]), "h264", 0),
    ),
    # Profundidad de color / HDR
    TestCase(
        "prof",
        "h265",
        "1080p",
        "10bit",
        cmd_estandar(fuente("gradients", RES["1080p"]), "h265", pix_fmt="yuv420p10le"),
    ),
    TestCase(
        "hdr",
        "h265",
        "1080p",
        "hdr",
        cmd_hdr(fuente("gradients", RES["1080p"]), "h265"),
    ),
    # Audio
    TestCase(
        "multi",
        "h264",
        "720p",
        "audiomultipista",
        cmd_multiaudio(fuente("testsrc", RES["720p"]), "h264"),
    ),
    # Archivo dañado
    TestCase(
        "trunc",
        "h264",
        "720p",
        "archivotruncado",
        cmd_estandar(fuente("testsrc", RES["720p"]), "h264"),
        post_procesado=truncar_archivo,
    ),
]


def generar_caso(caso: TestCase, destino: Path) -> None:
    nombre_archivo = (
        f"{caso.nombre_corto}_{caso.codec}_{caso.resolucion}_{caso.patron}.{caso.ext}"
    )
    salida = destino / nombre_archivo
    comando = caso.build_cmd(salida)
    try:
        subprocess.run(comando, check=True, capture_output=True, text=True)
        if caso.post_procesado:
            caso.post_procesado(salida)
        logger.info("Generado: %s", salida.name)
    except subprocess.CalledProcessError as exc:
        logger.error("Fallo al generar %s: %s", nombre_archivo, exc.stderr.strip())


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    for caso in CASOS:
        generar_caso(caso, OUTPUT_DIR)


if __name__ == "__main__":
    main()
