"""Fixtures compartidas de los tests end-to-end de la CLI de pyMedia.

Genera medios sintéticos diminutos con ffmpeg (mismo estilo que
`scripts/fixtures`) y fuerza el catálogo `en` para que las aserciones sobre
mensajes visibles no dependan del idioma del sistema.
"""

import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from pymedia.locale_manager import locale_manager

# `-g 10` fuerza un keyframe por segundo (vídeo a 10 fps): sin él, el
# segmentador de `split` no puede cortar en la marca indicada.
VIDEO_ARGS: list[str] = [
    "-c:v",
    "libx264",
    "-preset",
    "ultrafast",
    "-g",
    "10",
    "-pix_fmt",
    "yuv420p",
]

SRT_SPA = "1\n00:00:00,000 --> 00:00:01,000\nHola prueba\n"
SRT_ENG = "1\n00:00:00,000 --> 00:00:01,000\nHello test\n"


def _run_ffmpeg(args: list[str]) -> None:
    """Ejecuta ffmpeg de forma síncrona y aborta el test si falla.

    Args:
        args: Argumentos de ffmpeg, sin el binario ni flags globales.
    """
    cmd = ["ffmpeg", "-y", "-v", "error", *args]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if result.returncode != 0:
        pytest.fail(f"ffmpeg failed generating fixture: {result.stderr}")


@pytest.fixture(autouse=True)
def english_locale() -> None:
    """Fuerza el idioma `en` para que los mensajes de error sean estables."""
    locale_manager.set_language("en")


@pytest.fixture
def runner() -> CliRunner:
    """CliRunner para invocar la CLI tal como lo haría un usuario."""
    return CliRunner()


@pytest.fixture(scope="session")
def inputs_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Directorio de sesión con los medios sintéticos de entrada."""
    return tmp_path_factory.mktemp("cli_e2e_inputs")


@pytest.fixture(scope="session")
def video_mp4_a(inputs_dir: Path) -> Path:
    """Vídeo mp4 de 2 s (h264 + aac) con tono de 440 Hz."""
    output = inputs_dir / "video_a.mp4"
    _run_ffmpeg(
        [
            "-f",
            "lavfi",
            "-i",
            "testsrc2=size=160x90:rate=10:duration=2",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:duration=2",
            *VIDEO_ARGS,
            "-c:a",
            "aac",
            str(output),
        ]
    )
    return output


@pytest.fixture(scope="session")
def video_mp4_b(inputs_dir: Path) -> Path:
    """Vídeo mp4 de 2 s (h264 + aac) con tono de 523 Hz."""
    output = inputs_dir / "video_b.mp4"
    _run_ffmpeg(
        [
            "-f",
            "lavfi",
            "-i",
            "testsrc2=size=160x90:rate=10:duration=2",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=523:duration=2",
            *VIDEO_ARGS,
            "-c:a",
            "aac",
            str(output),
        ]
    )
    return output


@pytest.fixture(scope="session")
def video_mkv(inputs_dir: Path) -> Path:
    """Vídeo mkv de 2 s (h264 + aac), base de la familia de audio/subtítulos."""
    output = inputs_dir / "video.mkv"
    _run_ffmpeg(
        [
            "-f",
            "lavfi",
            "-i",
            "testsrc2=size=160x90:rate=10:duration=2",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:duration=2",
            *VIDEO_ARGS,
            "-c:a",
            "aac",
            str(output),
        ]
    )
    return output


@pytest.fixture(scope="session")
def video_mkv_subs(inputs_dir: Path) -> Path:
    """Vídeo mkv de 2 s con dos pistas de subtítulos srt (spa y eng)."""
    subs_spa = inputs_dir / "track_spa.srt"
    subs_spa.write_text(SRT_SPA, encoding="utf-8")
    subs_eng = inputs_dir / "track_eng.srt"
    subs_eng.write_text(SRT_ENG, encoding="utf-8")

    output = inputs_dir / "video_subs.mkv"
    _run_ffmpeg(
        [
            "-f",
            "lavfi",
            "-i",
            "testsrc2=size=160x90:rate=10:duration=2",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:duration=2",
            "-i",
            str(subs_spa),
            "-i",
            str(subs_eng),
            "-map",
            "0:v",
            "-map",
            "1:a",
            "-map",
            "2",
            "-map",
            "3",
            *VIDEO_ARGS,
            "-c:a",
            "aac",
            "-c:s",
            "srt",
            "-metadata:s:s:0",
            "language=spa",
            "-metadata:s:s:1",
            "language=eng",
            str(output),
        ]
    )
    return output


@pytest.fixture(scope="session")
def video_no_audio(inputs_dir: Path) -> Path:
    """Vídeo mp4 de 2 s sin pistas de audio."""
    output = inputs_dir / "video_no_audio.mp4"
    _run_ffmpeg(
        [
            "-f",
            "lavfi",
            "-i",
            "testsrc2=size=160x90:rate=10:duration=2",
            *VIDEO_ARGS,
            str(output),
        ]
    )
    return output


@pytest.fixture(scope="session")
def video_scenes(inputs_dir: Path) -> Path:
    """Vídeo mp4 de 3 s con tres bloques de color (dos cortes de escena)."""
    output = inputs_dir / "video_scenes.mp4"
    _run_ffmpeg(
        [
            "-f",
            "lavfi",
            "-i",
            "color=c=red:size=160x90:rate=10:duration=1",
            "-f",
            "lavfi",
            "-i",
            "color=c=blue:size=160x90:rate=10:duration=1",
            "-f",
            "lavfi",
            "-i",
            "color=c=green:size=160x90:rate=10:duration=1",
            "-filter_complex",
            "[0:v][1:v][2:v]concat=n=3:v=1:a=0[out]",
            "-map",
            "[out]",
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",
            "-pix_fmt",
            "yuv420p",
            str(output),
        ]
    )
    return output


@pytest.fixture(scope="session")
def audio_m4a(inputs_dir: Path) -> Path:
    """Pista de audio aac de 1 s."""
    output = inputs_dir / "audio.m4a"
    _run_ffmpeg(
        [
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:duration=1",
            "-c:a",
            "aac",
            str(output),
        ]
    )
    return output


@pytest.fixture(scope="session")
def audio_opus(inputs_dir: Path) -> Path:
    """Pista de audio opus de 1 s."""
    output = inputs_dir / "audio.opus"
    _run_ffmpeg(
        [
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:duration=1",
            "-c:a",
            "libopus",
            str(output),
        ]
    )
    return output


@pytest.fixture(scope="session")
def subs_spa(inputs_dir: Path) -> Path:
    """Fichero srt válido con un evento de subtítulo."""
    output = inputs_dir / "subs_spa.srt"
    output.write_text(SRT_SPA, encoding="utf-8")
    return output


@pytest.fixture(scope="session")
def subs_bad(inputs_dir: Path) -> Path:
    """Fichero con extensión srt pero contenido que no es un subtítulo."""
    output = inputs_dir / "subs_bad.srt"
    output.write_text("this is not a subtitles file", encoding="utf-8")
    return output
