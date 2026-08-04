"""Genera fixtures de vídeo para tests con ffmpeg.

Ejecutar: uv run tests/utils/generate_test_videos.py

Crea 15 archivos en tests/fixtures/:
  - valid_concat/   : 3 vídeos con parámetros idénticos (unibles con -c copy)
  - valid_encode/: 6 vídeos con parámetros variados (join requiere encode)
  - invalid/        : 6 archivos defectuosos para testear validación
"""

from __future__ import annotations

import random
import subprocess
import sys
from pathlib import Path

FIXTURES: Path = Path(__file__).resolve().parent.parent / "fixtures"


# ─────────────────────────── helpers ────────────────────────────


def _ffmpeg(args: list[str]) -> None:
    """Ejecuta ffmpeg con flags comunes. Lanza excepción si falla."""
    cmd: list[str] = ["ffmpeg", "-y", "-loglevel", "error", *args]
    subprocess.run(cmd, check=True)


def _ensure_dirs() -> None:
    """Crea la estructura de carpetas de fixtures."""
    for sub in ("valid_concat", "valid_encode", "invalid"):
        (FIXTURES / sub).mkdir(parents=True, exist_ok=True)


# ──────────────────────── vídeos válidos ────────────────────────


def _gen_concat() -> None:
    """3 vídeos idénticos en parámetros → join con -c copy.

    Solo varía el patrón visual de testsrc para distinguirlos.
    """
    patterns: list[str] = ["testsrc", "smptebars", "testsrc2"]
    for i, pattern in enumerate(patterns, start=1):
        out: Path = FIXTURES / "valid_concat" / f"clip_{i:02d}.mp4"
        _ffmpeg(
            [
                "-f",
                "lavfi",
                "-i",
                f"{pattern}=size=640x360:rate=30",
                "-f",
                "lavfi",
                "-i",
                "anullsrc=r=44100:cl=mono",
                "-t",
                "3",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-shortest",
                str(out),
            ]
        )


def _gen_encode() -> None:
    """6 vídeos con parámetros variados → join requiere encode.

    Variaciones: resolución, fps, codec de audio, sample rate, canales.
    """
    random.seed(42)
    specs: list[tuple[int, int, int, str, int, str]] = [
        # (width, height, fps, audio_codec, sample_rate, channels)
        (640, 360, 24, "aac", 48000, "stereo"),
        (1280, 720, 30, "aac", 44100, "mono"),
        (1920, 1080, 60, "libmp3lame", 48000, "stereo"),
        (640, 480, 25, "aac", 22050, "mono"),
        (1280, 720, 24, "libmp3lame", 44100, "stereo"),
        (854, 480, 30, "aac", 48000, "mono"),
    ]
    for i, (w, h, fps, acodec, arate, achan) in enumerate(specs, start=4):
        out: Path = FIXTURES / "valid_encode" / f"clip_{i:02d}.mp4"
        _ffmpeg(
            [
                "-f",
                "lavfi",
                "-i",
                f"testsrc=size={w}x{h}:rate={fps}",
                "-f",
                "lavfi",
                "-i",
                f"anullsrc=r={arate}:cl={achan}",
                "-t",
                "3",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                acodec,
                "-shortest",
                str(out),
            ]
        )


# ──────────────────────── vídeos inválidos ──────────────────────


def _gen_invalid() -> None:
    """6 archivos defectuosos para testear validación."""
    base: Path = FIXTURES / "invalid"

    # 1. Archivo vacío (0 bytes)
    (base / "empty.mp4").write_bytes(b"")

    # 2. Texto plano con extensión engañosa
    (base / "not_video.mp4").write_text("esto no es un vídeo", encoding="utf-8")

    # 3. Bytes aleatorios puros (sin estructura de contenedor)
    random.seed(99)
    random_bytes: bytes = bytes(random.randint(0, 255) for _ in range(4096))
    (base / "random_bytes.mp4").write_bytes(random_bytes)

    # 4. Vídeo válido truncado a mitad (header ok, cuerpo cortado)
    truncated_src: Path = FIXTURES / "valid_concat" / "clip_01.mp4"
    if truncated_src.exists():
        full: bytes = truncated_src.read_bytes()
        # Mantener primer 25% del archivo (header + algo de moov)
        (base / "corrupt_truncated.mp4").write_bytes(full[: len(full) // 4])
    else:
        # Fallback: si no existe clip_01, generar bytes parciales
        (base / "corrupt_truncated.mp4").write_bytes(random_bytes[:1024])

    # 5. Solo audio con extensión .mp4 (sin pista de vídeo)
    audio_only: Path = base / "audio_only.mp4"
    _ffmpeg(
        [
            "-f",
            "lavfi",
            "-i",
            "anullsrc=r=44100:cl=mono",
            "-t",
            "2",
            "-c:a",
            "aac",
            str(audio_only),
        ]
    )

    # 6. Imagen JPEG disfrazada con extensión .mp4
    jpeg_src: Path = base / "_temp.jpg"
    _ffmpeg(
        [
            "-f",
            "lavfi",
            "-i",
            "color=c=red:s=320x240:d=1",
            "-frames:v",
            "1",
            "-f",
            "image2",
            str(jpeg_src),
        ]
    )
    jpeg_bytes: bytes = jpeg_src.read_bytes()
    (base / "image_as_video.mp4").write_bytes(jpeg_bytes)
    jpeg_src.unlink()


# ──────────────────────────── main ──────────────────────────────


def main() -> None:
    """Genera todos los fixtures."""
    # Verificar que ffmpeg está disponible
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: ffmpeg no está instalado o no está en PATH.", file=sys.stderr)
        sys.exit(1)

    _ensure_dirs()
    _gen_concat()
    _gen_encode()
    _gen_invalid()

    total: int = sum(
        1 for f in FIXTURES.rglob("*") if f.is_file() and not f.name.startswith("_")
    )
    print(f"Fixtures generados en {FIXTURES} ({total} archivos)")


if __name__ == "__main__":
    main()
