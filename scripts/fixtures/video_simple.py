"""Genera un vídeo de prueba con un fractal de Mandelbrot y audio tonal."""

from dataclasses import dataclass
from pathlib import Path

from _common import (
    DURATION_SECONDS,
    FIXTURES_DIR,
    FPS,
    RESOLUTION,
    print_generated,
    run_ffmpeg,
)


@dataclass(frozen=True, slots=True)
class VideoSpec:
    """Parámetros de generación del vídeo de prueba.

    Attributes:
        filename: Nombre del fichero de salida.
        video_codec: Encoder de vídeo de ffmpeg.
        crf: Calidad (más bajo = más calidad y más tamaño).
        preset: Preset del encoder.
        maxiter: Iteraciones máximas del fractal (más detalle, más CPU).
        audio_codec: Encoder de audio de ffmpeg.
        audio_bitrate: Bitrate de audio.
        audio_frequency: Frecuencia del tono en Hz.
        audio_sample_rate: Frecuencia de muestreo en Hz.
    """

    filename: str = "simple.mp4"
    video_codec: str = "libsvtav1"
    crf: int = 30
    preset: int = 8
    maxiter: int = 200
    audio_codec: str = "aac"
    audio_bitrate: str = "128k"
    audio_frequency: int = 440
    audio_sample_rate: int = 48000


SPEC = VideoSpec()


def build_ffmpeg_args(spec: VideoSpec, output: Path) -> list[str]:
    """Construye los argumentos de ffmpeg para el vídeo de prueba.

    Args:
        spec: Parámetros de generación.
        output: Ruta del fichero de salida.

    Returns:
        Argumentos de ffmpeg (sin el ejecutable).
    """
    fractal = f"mandelbrot=size={RESOLUTION}:rate={FPS}:maxiter={spec.maxiter}"
    # Zoom suave y continuo sobre el fractal.
    zoom = (
        "zoompan=z='min(zoom+0.0015,2.5)':"
        "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d=1:s={RESOLUTION}:fps={FPS}"
    )
    video_filter = (
        f"{fractal},{zoom},trim=duration={DURATION_SECONDS},setpts=PTS-STARTPTS"
    )
    audio_filter = (
        f"sine=frequency={spec.audio_frequency}:"
        f"sample_rate={spec.audio_sample_rate}:duration={DURATION_SECONDS}"
    )

    args = ["-f", "lavfi", "-i", video_filter]
    args += ["-f", "lavfi", "-i", audio_filter]
    args += ["-c:v", spec.video_codec, "-crf", str(spec.crf)]
    args += ["-preset", str(spec.preset)]
    args += ["-c:a", spec.audio_codec, "-b:a", spec.audio_bitrate]
    args += ["-t", str(DURATION_SECONDS)]
    args += ["-movflags", "+faststart"]  # reproducción progresiva del MP4
    args.append(str(output))
    return args


def generate(output_dir: Path = FIXTURES_DIR) -> list[Path]:
    """Genera el vídeo de prueba.

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
