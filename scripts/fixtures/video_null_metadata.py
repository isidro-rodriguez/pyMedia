"""Genera un vídeo de test con metadatos de stream nulos.

Produce un MKV de 30 s, 1280x720, con 6 pistas de audio y 6 de
subtítulos, sin title/language/disposition en ningún stream. Pensado
para comprobar que pymedia no rompe con vídeos válidos pero con
metadatos ausentes.
"""

import tempfile
from pathlib import Path

from _common import (
    DURATION_SECONDS,
    FIXTURES_DIR,
    FPS,
    RESOLUTION,
    print_generated,
    run_ffmpeg,
)

OUTPUT_NAME = "test_null_metadata.mkv"
AUDIO_TRACKS = 6
SUBTITLE_TRACKS = 6

SRT_TEMPLATE = "1\n00:00:00,000 --> 00:00:{duration:02d},000\nTest subtitle {index}\n"


def build_subtitle_files(tmpdir: Path) -> list[Path]:
    """Crea ficheros .srt mínimos, uno por pista de subtítulos.

    Args:
        tmpdir: Directorio donde crear los ficheros.

    Returns:
        Rutas de los ficheros `.srt` creados, en orden.
    """
    paths: list[Path] = []
    for i in range(SUBTITLE_TRACKS):
        path = tmpdir / f"sub_{i}.srt"
        path.write_text(
            SRT_TEMPLATE.format(duration=DURATION_SECONDS, index=i),
            encoding="utf-8",
        )
        paths.append(path)
    return paths


def build_ffmpeg_args(subtitle_files: list[Path], output: Path) -> list[str]:
    """Ensambla los argumentos de ffmpeg: inputs, mapeo y limpieza de metadatos.

    Args:
        subtitle_files: Ficheros `.srt` a incrustar.
        output: Ruta del fichero de salida.

    Returns:
        Argumentos de ffmpeg (sin el ejecutable).
    """
    video = f"testsrc2=size={RESOLUTION}:rate={FPS}:duration={DURATION_SECONDS}"
    args = ["-f", "lavfi", "-i", video]

    # Un tono distinto por pista de audio, solo para diferenciarlas.
    for i in range(AUDIO_TRACKS):
        tone = f"sine=frequency={220 + i * 110}:duration={DURATION_SECONDS}"
        args += ["-f", "lavfi", "-i", tone]

    for path in subtitle_files:
        args += ["-i", str(path)]

    # Mapeo: 1 vídeo + N audio + N subtítulos.
    args += ["-map", "0:v"]
    for i in range(AUDIO_TRACKS):
        args += ["-map", f"{i + 1}:a"]
    for i in range(SUBTITLE_TRACKS):
        args += ["-map", f"{AUDIO_TRACKS + 1 + i}:s"]

    args += ["-c:v", "libx264", "-pix_fmt", "yuv420p"]
    args += ["-c:a", "aac", "-b:a", "128k"]
    args += ["-c:s", "srt"]

    # Sin metadata copiada del input ni capítulos.
    args += ["-map_metadata", "-1", "-map_chapters", "-1"]

    # ffmpeg/libx264/aac inyectan un tag "encoder" aunque no se pida;
    # se vacía para que no quede como único metadato "vivo".
    args += ["-metadata:s:v:0", "encoder="]
    for i in range(AUDIO_TRACKS):
        args += [f"-metadata:s:a:{i}", "encoder="]

    # ffmpeg marca "default" la primera pista de cada tipo; se resetea
    # a 0 en todas para que la disposition quede nula.
    args += ["-disposition:v:0", "0"]
    for i in range(AUDIO_TRACKS):
        args += [f"-disposition:a:{i}", "0"]
    for i in range(SUBTITLE_TRACKS):
        args += [f"-disposition:s:{i}", "0"]

    args.append(str(output))
    return args


def generate(output_dir: Path = FIXTURES_DIR) -> list[Path]:
    """Genera el vídeo de test con metadatos nulos.

    Args:
        output_dir: Directorio raíz de fixtures.

    Returns:
        Rutas de los ficheros generados.

    Raises:
        FixtureGenerationError: Si ffmpeg falla.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / OUTPUT_NAME

    with tempfile.TemporaryDirectory() as tmp:
        subtitle_files = build_subtitle_files(Path(tmp))
        run_ffmpeg(build_ffmpeg_args(subtitle_files, output))
    return [output]


def main() -> None:
    """Genera los fixtures en el directorio por defecto."""
    print_generated(generate())


if __name__ == "__main__":
    main()
