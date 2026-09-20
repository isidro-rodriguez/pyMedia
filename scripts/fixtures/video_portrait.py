"""Genera un vídeo de prueba en formato vertical (9:16) para móviles."""

from dataclasses import dataclass
from pathlib import Path

from _common import DURATION_SECONDS, FIXTURES_DIR, FPS, print_generated, run_ffmpeg


@dataclass(frozen=True, slots=True)
class PortraitSpec:
    """Parámetros del vídeo vertical de prueba.

    Attributes:
        filename: Nombre del fichero de salida.
        width: Ancho en píxeles (menor que el alto).
        height: Alto en píxeles.
        video_codec: Encoder de vídeo de ffmpeg.
        crf: Calidad (más bajo = más calidad y más tamaño).
        audio_codec: Encoder de audio de ffmpeg.
        audio_bitrate: Bitrate de audio.
        audio_frequency: Frecuencia del tono en Hz.
    """

    filename: str = "portrait.mp4"
    width: int = 720
    height: int = 1280
    video_codec: str = "libx264"
    crf: int = 23
    audio_codec: str = "aac"
    audio_bitrate: str = "128k"
    audio_frequency: int = 440


SPEC = PortraitSpec()


def build_ffmpeg_args(spec: PortraitSpec, output: Path) -> list[str]:
    """Construye los argumentos de ffmpeg para el vídeo vertical.

    Args:
        spec: Parámetros de generación.
        output: Ruta del fichero de salida.

    Returns:
        Argumentos de ffmpeg (sin el ejecutable).
    """
    size = f"{spec.width}x{spec.height}"
    video = f"testsrc2=size={size}:rate={FPS}:duration={DURATION_SECONDS}"
    audio = f"sine=frequency={spec.audio_frequency}:duration={DURATION_SECONDS}"

    args = ["-f", "lavfi", "-i", video]
    args += ["-f", "lavfi", "-i", audio]
    args += ["-c:v", spec.video_codec, "-crf", str(spec.crf)]
    args += ["-pix_fmt", "yuv420p", "-vf", "setsar=1"]  # compatible con móviles
    args += ["-c:a", spec.audio_codec, "-b:a", spec.audio_bitrate]
    args += ["-movflags", "+faststart"]
    args.append(str(output))
    return args


def generate(output_dir: Path = FIXTURES_DIR) -> list[Path]:
    """Genera el vídeo vertical de prueba.

    Args:
        output_dir: Directorio raíz de fixtures.

    Returns:
        Rutas de los ficheros generados.

    Raises:
        FixtureGenerationError: Si ffmpeg falla.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / SPEC.filename
    run_ffmpeg(build_ffmpeg_args(SPEC, output))
    return [output]


def main() -> None:
    """Genera los fixtures en el directorio por defecto."""
    print_generated(generate())


if __name__ == "__main__":
    main()
