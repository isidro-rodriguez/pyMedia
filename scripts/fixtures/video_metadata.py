"""Genera un MKV de prueba con 6 pistas de audio y 6 de subtítulos con metadatos."""

import tempfile
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

OUTPUT_NAME = "metadata.mkv"

ASS_TEMPLATE = """[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, \
OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, \
ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, \
MarginR, MarginV, Encoding
Style: Default,Arial,36,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,\
100,100,0,0,1,2,2,2,10,10,50,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:30.00,Default,,0,0,0,,Subtitulo: {text}
"""


@dataclass(frozen=True, slots=True)
class AudioSpec:
    """Pista de audio del vídeo de prueba.

    Attributes:
        language: Código de idioma ISO 639-2.
        title: Título de la pista.
        codec: Encoder de ffmpeg.
        bitrate: Bitrate de audio.
        channels: Número de canales.
        frequency: Frecuencia del tono en Hz.
    """

    language: str
    title: str
    codec: str
    bitrate: str
    channels: int
    frequency: int


@dataclass(frozen=True, slots=True)
class SubtitleSpec:
    """Pista de subtítulos del vídeo de prueba.

    Attributes:
        language: Código de idioma ISO 639-2.
        title: Título de la pista (y texto mostrado).
    """

    language: str
    title: str


AUDIO_TRACKS: tuple[AudioSpec, ...] = (
    AudioSpec("spa", "Español (AAC Stereo)", "aac", "128k", 2, 440),
    AudioSpec("eng", "English (AC3 5.1)", "ac3", "384k", 6, 440),
    AudioSpec("fra", "Français (MP3 Stereo)", "mp3", "192k", 2, 440),
    AudioSpec("deu", "Deutsch (Opus Mono)", "libopus", "96k", 1, 880),
    AudioSpec("ita", "Italiano (FLAC Stereo)", "flac", "300k", 2, 880),
    AudioSpec("por", "Português (E-AC3 5.1)", "eac3", "448k", 6, 880),
)

SUBTITLE_TRACKS: tuple[SubtitleSpec, ...] = (
    SubtitleSpec("spa", "Español"),
    SubtitleSpec("eng", "English"),
    SubtitleSpec("fra", "Français"),
    SubtitleSpec("deu", "Deutsch"),
    SubtitleSpec("ita", "Italiano"),
    SubtitleSpec("por", "Português"),
)


def build_subtitle_files(tmpdir: Path) -> list[Path]:
    """Crea los .ass temporales, uno por pista de subtítulos.

    Args:
        tmpdir: Directorio donde crear los ficheros.

    Returns:
        Rutas de los ficheros `.ass` creados, en orden.
    """
    paths: list[Path] = []
    for spec in SUBTITLE_TRACKS:
        path = tmpdir / f"sub_{spec.language}.ass"
        path.write_text(ASS_TEMPLATE.format(text=spec.title), encoding="utf-8")
        paths.append(path)
    return paths


def build_ffmpeg_args(subtitle_files: list[Path], output: Path) -> list[str]:
    """Ensambla los argumentos de ffmpeg: inputs, mapeo, códecs y metadatos.

    Args:
        subtitle_files: Ficheros `.ass` a incrustar.
        output: Ruta del fichero de salida.

    Returns:
        Argumentos de ffmpeg (sin el ejecutable).
    """
    # Inputs: vídeo, un tono por pista de audio, un fichero por subtítulo.
    testsrc = f"testsrc=duration={DURATION_SECONDS}:size={RESOLUTION}:rate={FPS}"
    args = ["-f", "lavfi", "-i", testsrc]
    for audio in AUDIO_TRACKS:
        tone = f"sine=frequency={audio.frequency}:duration={DURATION_SECONDS}"
        args += ["-f", "lavfi", "-i", tone]
    for path in subtitle_files:
        args += ["-i", str(path)]

    # Mapeo: 1 vídeo + N audio + N subtítulos.
    args += ["-map", "0:v:0"]
    for i in range(len(AUDIO_TRACKS)):
        args += ["-map", f"{i + 1}:a:0"]
    subtitle_offset = 1 + len(AUDIO_TRACKS)
    for i in range(len(subtitle_files)):
        args += ["-map", f"{subtitle_offset + i}:s:0"]

    args += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:s", "ass"]

    for i, audio in enumerate(AUDIO_TRACKS):
        args += [f"-c:a:{i}", audio.codec, f"-b:a:{i}", audio.bitrate]
        args += [f"-ac:a:{i}", str(audio.channels)]
        args += [f"-metadata:s:a:{i}", f"language={audio.language}"]
        args += [f"-metadata:s:a:{i}", f"title={audio.title}"]

    for i, subtitle in enumerate(SUBTITLE_TRACKS):
        args += [f"-metadata:s:s:{i}", f"language={subtitle.language}"]
        args += [f"-metadata:s:s:{i}", f"title={subtitle.title}"]

    args += ["-write_crc32", "1", str(output)]
    return args


def generate(output_dir: Path = FIXTURES_DIR) -> list[Path]:
    """Genera el vídeo de prueba con metadatos completos.

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
