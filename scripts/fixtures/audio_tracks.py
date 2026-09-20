"""Genera pistas de audio de prueba.

Pistas de audio de 30 segundos en formatos compatibles con
.mp4, .mkv y .webm, para probar los comandos `add-audio` / `edit-audio`.
"""

import subprocess
from dataclasses import dataclass
from pathlib import Path

DURATION_SECONDS = 30
OUTPUT_DIR = Path("audio_test")


@dataclass(frozen=True, slots=True)
class TrackSpec:
    """Especificación de una pista de audio de prueba a generar.

    Attributes:
        filename: Nombre del fichero de salida.
        codec: Códec de audio a usar (nombre del encoder de ffmpeg).
        frequency: Frecuencia del tono senoidal en Hz.
        language: Código de idioma ISO 639-2/B a insertar como metadato.
        title: Título de la pista.
        compatible_with: Contenedores donde esta pista es válida.
    """

    filename: str
    codec: str
    frequency: int
    language: str
    title: str
    compatible_with: tuple[str, ...]


TRACKS: tuple[TrackSpec, ...] = (
    TrackSpec(
        filename="track_aac.m4a",
        codec="aac",
        frequency=440,
        language="eng",
        title="AAC Test Track",
        compatible_with=(".mp4", ".mkv"),
    ),
    TrackSpec(
        filename="track_ac3.ac3",
        codec="ac3",
        frequency=523,
        language="spa",
        title="AC3 Test Track",
        compatible_with=(".mkv",),
    ),
    TrackSpec(
        filename="track_opus.opus",
        codec="libopus",
        frequency=659,
        language="fra",
        title="Opus Test Track",
        compatible_with=(".mkv", ".webm"),
    ),
    TrackSpec(
        filename="track_vorbis.ogg",
        codec="libvorbis",
        frequency=784,
        language="deu",
        title="Vorbis Test Track",
        compatible_with=(".mkv", ".webm"),
    ),
)


def build_track(spec: TrackSpec, output_dir: Path) -> Path:
    """Genera un fichero de audio de prueba con ffmpeg.

    Args:
        spec: Especificación de la pista a generar.
        output_dir: Directorio donde escribir el fichero resultante.

    Returns:
        Ruta del fichero de audio generado.

    Raises:
        subprocess.CalledProcessError: Si ffmpeg falla al generar la pista.
    """
    output_path = output_dir / spec.filename
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"sine=frequency={spec.frequency}:duration={DURATION_SECONDS}",
        "-c:a",
        spec.codec,
        "-metadata",
        f"language={spec.language}",
        "-metadata",
        f"title={spec.title}",
        str(output_path),
    ]
    subprocess.run(cmd, capture_output=True, text=True, check=True)
    return output_path


def main() -> None:
    """Genera todas las pistas de prueba definidas en TRACKS."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for spec in TRACKS:
        try:
            path = build_track(spec=spec, output_dir=OUTPUT_DIR)
        except subprocess.CalledProcessError as err:
            print(f"[ERROR] {spec.filename}: {err.stderr}")
            continue
        containers = ", ".join(spec.compatible_with)
        print(f"[OK] {path} ({spec.codec}, {containers})")


if __name__ == "__main__":
    main()
