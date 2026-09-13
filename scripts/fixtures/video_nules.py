"""Genera un vídeo de test con metadatos de stream nulos.

Produce un MKV de 30s, 1280x720, con 6 pistas de audio y 6 de
subtítulos, sin title/language/disposition en ningún stream. Pensado
para comprobar que pymedia no rompe con vídeos válidos pero con
metadatos ausentes.
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

DURATION = 30
RESOLUTION = "1280x720"
FPS = 30
AUDIO_TRACKS = 6
SUBTITLE_TRACKS = 6
OUTPUT = Path("../../.local/fixtures/test_null_metadata.mkv")

SRT_TEMPLATE = "1\n00:00:00,000 --> 00:00:{duration:02d},000\nTest subtitle {index}\n"


def build_subtitle_files(tmpdir: Path) -> list[Path]:
    """Crea ficheros .srt mínimos, uno por pista de subtítulos."""
    paths = []
    for i in range(SUBTITLE_TRACKS):
        srt_path = tmpdir / f"sub_{i}.srt"
        srt_path.write_text(SRT_TEMPLATE.format(duration=DURATION, index=i))
        paths.append(srt_path)
    return paths


def build_ffmpeg_command(subtitle_files: list[Path]) -> list[str]:
    """Construye el comando ffmpeg: inputs, mapeo y limpieza de metadatos."""
    cmd = ["ffmpeg", "-y"]

    # Vídeo sintético
    cmd += [
        "-f",
        "lavfi",
        "-i",
        f"testsrc2=size={RESOLUTION}:rate={FPS}:duration={DURATION}",
    ]

    # Un tono distinto por pista de audio, solo para diferenciarlas
    for i in range(AUDIO_TRACKS):
        freq = 220 + i * 110
        cmd += ["-f", "lavfi", "-i", f"sine=frequency={freq}:duration={DURATION}"]

    # Subtítulos
    for srt in subtitle_files:
        cmd += ["-i", str(srt)]

    # Mapeo: 1 vídeo + N audio + N subs
    cmd += ["-map", "0:v"]
    for i in range(AUDIO_TRACKS):
        cmd += ["-map", f"{i + 1}:a"]
    for i in range(SUBTITLE_TRACKS):
        cmd += ["-map", f"{AUDIO_TRACKS + 1 + i}:s"]

    # Códecs
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p"]
    cmd += ["-c:a", "aac", "-b:a", "128k"]
    cmd += ["-c:s", "srt"]

    # Sin metadata copiada del input ni capítulos
    cmd += ["-map_metadata", "-1", "-map_chapters", "-1"]

    # ffmpeg/libx264/aac inyectan un tag "encoder" aunque no se pida;
    # se vacía explícitamente para que no quede como único metadato "vivo"
    cmd += ["-metadata:s:v:0", "encoder="]
    for i in range(AUDIO_TRACKS):
        cmd += [f"-metadata:s:a:{i}", "encoder="]
        cmd += [f"-disposition:a:{i}", "0"]

    # ffmpeg marca "default" en la primera pista de cada tipo por defecto;
    # se resetea a 0 en todas para que la disposition quede nula
    cmd += ["-disposition:v:0", "0"]
    for i in range(SUBTITLE_TRACKS):
        cmd += [f"-disposition:s:{i}", "0"]

    cmd.append(str(OUTPUT))
    return cmd


def main() -> None:
    """Genera los subtítulos temporales y ejecuta ffmpeg."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        subtitle_files = build_subtitle_files(tmp_path)
        cmd = build_ffmpeg_command(subtitle_files)
        subprocess.run(cmd, check=True)
    print(f"Generado: {OUTPUT.resolve()}")


if __name__ == "__main__":
    main()
