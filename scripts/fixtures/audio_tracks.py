"""Genera pistas de audio de prueba.

Pistas de 30 segundos en formatos compatibles con .mp4, .mkv y .webm,
para probar los comandos `add-audio` / `edit-audio`.
"""

from dataclasses import dataclass
from pathlib import Path

from _common import (
    DURATION_SECONDS,
    FIXTURES_DIR,
    print_generated,
    run_ffmpeg,
)

AUDIO_DIR_NAME = "audio"


@dataclass(frozen=True, slots=True)
class TrackSpec:
    """Especificación de una pista de audio de prueba a generar.

    Attributes:
        filename: Nombre del fichero de salida.
        codec: Códec de audio (nombre del encoder de ffmpeg).
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


def build_ffmpeg_args(spec: TrackSpec, output: Path) -> list[str]:
    """Construye los argumentos de ffmpeg para una pista.

    Args:
        spec: Especificación de la pista.
        output: Ruta del fichero de salida.

    Returns:
        Argumentos de ffmpeg (sin el ejecutable).
    """
    tone = f"sine=frequency={spec.frequency}:duration={DURATION_SECONDS}"
    args = ["-f", "lavfi", "-i", tone, "-c:a", spec.codec]
    args += ["-metadata", f"language={spec.language}"]
    args += ["-metadata", f"title={spec.title}"]
    args.append(str(output))
    return args


def generate(output_dir: Path = FIXTURES_DIR) -> list[Path]:
    """Genera todas las pistas definidas en `TRACKS`.

    Args:
        output_dir: Directorio raíz de fixtures.

    Returns:
        Rutas de los ficheros generados.

    Raises:
        FixtureGenerationError: Si ffmpeg falla en alguna pista.
    """
    audio_dir = output_dir / AUDIO_DIR_NAME
    audio_dir.mkdir(parents=True, exist_ok=True)

    paths: list[Path] = []
    for spec in TRACKS:
        output = audio_dir / spec.filename
        run_ffmpeg(build_ffmpeg_args(spec, output))
        paths.append(output)
    return paths


def main() -> None:
    """Genera los fixtures en el directorio por defecto."""
    print_generated(generate())


if __name__ == "__main__":
    main()
