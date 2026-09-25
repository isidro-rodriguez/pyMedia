"""Utilidades compartidas por los generadores de fixtures de test."""

import subprocess
from pathlib import Path

# Raíz de fixtures: <repo>/local/fixtures (los scripts viven a 2 niveles del repo).
FIXTURES_DIR = Path(__file__).resolve().parents[2] / "local" / "fixtures"

DURATION_SECONDS = 30
RESOLUTION = "1280x720"
FPS = 30


class FixtureGenerationError(RuntimeError):
    """Fallo al generar un fixture con ffmpeg."""


def run_ffmpeg(args: list[str]) -> None:
    """Ejecuta ffmpeg con las opciones comunes y lanza si falla.

    Args:
        args: Argumentos de ffmpeg, sin el ejecutable ni `-y`.

    Raises:
        FixtureGenerationError: Si ffmpeg termina con error.
    """
    command = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as err:
        msg = f"ffmpeg falló ({err.returncode}): {err.stderr.strip()}"
        raise FixtureGenerationError(msg) from err


def print_generated(paths: list[Path]) -> None:
    """Muestra por consola los ficheros generados.

    Args:
        paths: Rutas de los ficheros generados.
    """
    for path in paths:
        print(f"[OK] {path}")
