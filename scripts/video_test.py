"""Genera un vídeo de prueba con múltiples pistas de audio y subtítulos."""

import subprocess
from pathlib import Path

SUBTITLES = {
    "sub_es.ass": "Español",
    "sub_en.ass": "English",
    "sub_fr.ass": "Français",
    "sub_de.ass": "Deutsch",
    "sub_it.ass": "Italiano",
    "sub_pt.ass": "Português",
}

AUDIO_TITLES = {
    "spa": "Español (AAC Stereo)",
    "eng": "English (AC3 5.1)",
    "fra": "Français (MP3 Stereo)",
    "deu": "Deutsch (Opus Mono)",
    "ita": "Italiano (FLAC Stereo)",
    "por": "Português (E-AC3 5.1)",
}

SUBTITLE_TITLES = {
    "spa": "Español",
    "eng": "English",
    "fra": "Français",
    "deu": "Deutsch",
    "ita": "Italiano",
    "por": "Português",
}

ASS_TEMPLATE = """[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,36,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,50,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:30.00,Default,,0,0,0,,Subtitulo: {text}
"""


def build_subtitle_files(output_dir: Path) -> list[Path]:
    """Crea los .ass temporales y devuelve sus rutas en orden."""
    paths = []
    for filename, text in SUBTITLES.items():
        path = output_dir / filename
        path.write_text(ASS_TEMPLATE.format(text=text), encoding="utf-8")
        paths.append(path)
    return paths


def build_ffmpeg_command(sub_paths: list[Path], output: Path) -> list[str]:
    """Ensambla el comando ffmpeg completo."""
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "testsrc=duration=30:size=1280x720:rate=30",
        "-f", "lavfi", "-i", "sine=frequency=440:duration=30",
        "-f", "lavfi", "-i", "sine=frequency=880:duration=30",
    ]
    for sub_path in sub_paths:
        cmd += ["-i", str(sub_path)]

    cmd += [
        "-map", "0:v:0",
        "-map", "1:a:0", "-map", "1:a:0", "-map", "1:a:0",
        "-map", "2:a:0", "-map", "2:a:0", "-map", "2:a:0",
        "-map", "3:s:0", "-map", "4:s:0", "-map", "5:s:0",
        "-map", "6:s:0", "-map", "7:s:0", "-map", "8:s:0",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a:0", "aac", "-b:a:0", "128k", "-ac:a:0", "2",
        "-c:a:1", "ac3", "-b:a:1", "384k", "-ac:a:1", "6",
        "-c:a:2", "mp3", "-b:a:2", "192k", "-ac:a:2", "2",
        "-c:a:3", "libopus", "-b:a:3", "96k", "-ac:a:3", "1",
        "-c:a:4", "flac", "-b:a:4", "300k", "-ac:a:4", "2",
        "-c:a:5", "eac3", "-b:a:5", "448k", "-ac:a:5", "6",
        "-c:s", "ass",
    ]

    for index, (lang, title) in enumerate(AUDIO_TITLES.items()):
        cmd += [f"-metadata:s:a:{index}", f"language={lang}"]
        cmd += [f"-metadata:s:a:{index}", f"title={title}"]

    for index, (lang, title) in enumerate(SUBTITLE_TITLES.items()):
        cmd += [f"-metadata:s:s:{index}", f"language={lang}"]
        cmd += [f"-metadata:s:s:{index}", f"title={title}"]

    cmd += ["-write_crc32", "1", str(output)]
    return cmd


def main() -> None:
    """Genera el vídeo de prueba y limpia los subtítulos temporales."""
    output_dir = Path.cwd()
    output = output_dir / "video_prueba.mkv"

    sub_paths = build_subtitle_files(output_dir)
    try:
        cmd = build_ffmpeg_command(sub_paths, output)
        subprocess.run(cmd, check=True, encoding="utf-8", errors="strict")
    finally:
        for path in sub_paths:
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
