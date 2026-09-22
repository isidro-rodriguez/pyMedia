"""Fixtures compartidas de los tests end-to-end de la CLI de pyMedia.

Genera medios sintéticos diminutos con ffmpeg (mismo estilo que
`scripts/fixtures`) y fuerza el catálogo `en` para que las aserciones sobre
mensajes visibles no dependan del idioma del sistema.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest
from helpers import CliResult, Invoke
from typer.testing import CliRunner

from pymedia.locale_manager import locale_manager
from pymedia.main import app

ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = ROOT / "scripts" / "build.py"
BINARY_NAME = "pymedia.exe" if sys.platform == "win32" else "pymedia"
BINARY_PATH = ROOT / "build" / BINARY_NAME

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
def video_mkv_default_audio(inputs_dir: Path) -> Path:
    """Vídeo mkv de 2 s cuya única pista de audio está marcada como `default`.

    A diferencia de `video_mkv`, ffmpeg aquí marca la pista con la disposición
    `default`, que es lo que activa el borrado del `default` anterior al añadir
    o editar una pista de audio.
    """
    output = inputs_dir / "video_default_audio.mkv"
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
            "-disposition:a:0",
            "default",
            str(output),
        ]
    )
    return output


@pytest.fixture(scope="session")
def video_mkv_two_audio(inputs_dir: Path) -> Path:
    """Vídeo mkv de 2 s con dos pistas de audio: la última `default` y `forced`."""
    output = inputs_dir / "video_two_audio.mkv"
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
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=523:duration=2",
            "-map",
            "0:v",
            "-map",
            "1:a",
            "-map",
            "2:a",
            *VIDEO_ARGS,
            "-c:a",
            "aac",
            "-disposition:a:0",
            "0",
            "-disposition:a:1",
            "default+forced",
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
def video_mp4_diff_res(inputs_dir: Path) -> Path:
    """Vídeo mp4 de 2 s con otra resolución (320x180)."""
    output = inputs_dir / "video_diff_res.mp4"
    _run_ffmpeg(
        [
            "-f",
            "lavfi",
            "-i",
            "testsrc2=size=320x180:rate=10:duration=2",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:duration=2",
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",
            "-g",
            "10",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            str(output),
        ]
    )
    return output


@pytest.fixture(scope="session")
def video_mp4_diff_codec(inputs_dir: Path) -> Path:
    """Vídeo mp4 de 2 s con otro códec (mpeg4)."""
    output = inputs_dir / "video_diff_codec.mp4"
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
            "-c:v",
            "mpeg4",
            "-preset",
            "ultrafast",
            "-g",
            "10",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            str(output),
        ]
    )
    return output


@pytest.fixture(scope="session")
def video_mp4_diff_fps(inputs_dir: Path) -> Path:
    """Vídeo mp4 de 2 s con otro fps (5)."""
    output = inputs_dir / "video_diff_fps.mp4"
    _run_ffmpeg(
        [
            "-f",
            "lavfi",
            "-i",
            "testsrc2=size=160x90:rate=5:duration=2",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:duration=2",
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",
            "-g",
            "10",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            str(output),
        ]
    )
    return output


@pytest.fixture(scope="session")
def video_mp4_diff_pixfmt(inputs_dir: Path) -> Path:
    """Vídeo mp4 de 2 s con otro pix_fmt (yuv422p)."""
    output = inputs_dir / "video_diff_pixfmt.mp4"
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
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",
            "-g",
            "10",
            "-pix_fmt",
            "yuv422p",
            "-c:a",
            "aac",
            str(output),
        ]
    )
    return output


@pytest.fixture(scope="session")
def video_mp4_diff_sr(inputs_dir: Path) -> Path:
    """Vídeo mp4 de 2 s con otra frecuencia de muestreo (48000 Hz)."""
    output = inputs_dir / "video_diff_sr.mp4"
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
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",
            "-g",
            "10",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-ar",
            "48000",
            str(output),
        ]
    )
    return output


@pytest.fixture(scope="session")
def video_mp4_diff_audio_codec(inputs_dir: Path) -> Path:
    """Vídeo mp4 de 2 s con códec de audio mp3."""
    output = inputs_dir / "video_diff_audio_codec.mp4"
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
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",
            "-g",
            "10",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "mp3",
            str(output),
        ]
    )
    return output


@pytest.fixture(scope="session")
def video_mp4_multi_audio(inputs_dir: Path) -> Path:
    """Vídeo mp4 de 2 s con 6 pistas de audio (para probar truncado)."""
    output = inputs_dir / "video_multi_audio.mp4"
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
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=523:duration=2",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=659:duration=2",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=784:duration=2",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=880:duration=2",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=988:duration=2",
            "-map",
            "0:v",
            "-map",
            "1:a",
            "-map",
            "2:a",
            "-map",
            "3:a",
            "-map",
            "4:a",
            "-map",
            "5:a",
            "-map",
            "6:a",
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",
            "-g",
            "10",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            str(output),
        ]
    )
    return output


@pytest.fixture(scope="session")
def video_webm_vp8(inputs_dir: Path) -> Path:
    """Vídeo webm de 2 s con códec vp8."""
    output = inputs_dir / "video_vp8.webm"
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
            "-c:v",
            "libvpx",
            "-preset",
            "ultrafast",
            "-g",
            "10",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "libopus",
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
def subs_ass(inputs_dir: Path, subs_spa: Path) -> Path:
    """Fichero ass válido: el srt convertido por ffmpeg al formato ass."""
    output = inputs_dir / "subs_spa.ass"
    _run_ffmpeg(["-i", str(subs_spa), str(output)])
    return output


@pytest.fixture(scope="session")
def subs_vtt(inputs_dir: Path, subs_spa: Path) -> Path:
    """Fichero vtt válido: el srt convertido por ffmpeg al formato webvtt."""
    output = inputs_dir / "subs_spa.vtt"
    _run_ffmpeg(["-i", str(subs_spa), str(output)])
    return output


@pytest.fixture(scope="session")
def subs_bad(inputs_dir: Path) -> Path:
    """Fichero con extensión srt pero contenido que no es un subtítulo."""
    output = inputs_dir / "subs_bad.srt"
    output.write_text("this is not a subtitles file", encoding="utf-8")
    return output


@pytest.fixture(scope="session")
def video_audio_only_mkv(inputs_dir: Path) -> Path:
    """Mkv de 2 s con un solo audio (aac), sin pista de vídeo."""
    output = inputs_dir / "video_audio_only.mkv"
    _run_ffmpeg(
        [
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:duration=2",
            "-c:a",
            "aac",
            "-map",
            "0:a",
            str(output),
        ]
    )
    return output


@pytest.fixture(scope="session")
def video_mkv_audio_mono(inputs_dir: Path) -> Path:
    """Vídeo mkv de 2 s con vídeo h264 y audio mono (aac, 1 canal)."""
    output = inputs_dir / "video_mkv_audio_mono.mkv"
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
            "-ac",
            "1",
            str(output),
        ]
    )
    return output


@pytest.fixture(scope="session")
def video_mkv_audio_stereo(inputs_dir: Path) -> Path:
    """Vídeo mkv de 2 s con vídeo h264 y audio estéreo (aac, 2 canales)."""
    output = inputs_dir / "video_mkv_audio_stereo.mkv"
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
            "-ac",
            "2",
            str(output),
        ]
    )
    return output


# =============================================================================
#  Ejecutores de pyMedia (CLI Typer y binario compilado)
# =============================================================================


@pytest.fixture(scope="session")
def empty_localedir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Directorio vacío que fuerza msgid en inglés dentro del binario."""
    return tmp_path_factory.mktemp("binary_empty_locales")


@pytest.fixture(scope="session")
def built_binary() -> Path:
    """Compila el ejecutable con el script oficial y devuelve su ruta.

    Solo se instancia si se seleccionan los tests `binary`, porque el build
    tarda minutos y `pymedia` lo pide de forma perezosa.
    """
    result = subprocess.run(
        [sys.executable, str(BUILD_SCRIPT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if result.returncode != 0:
        pytest.fail(
            f"build.py falló (exit {result.returncode}):\n"
            f"{result.stdout}\n{result.stderr}"
        )
    assert BINARY_PATH.is_file(), f"No se generó {BINARY_PATH}"
    assert BINARY_PATH.stat().st_size > 1_000_000, "El ejecutable parece incompleto"
    return BINARY_PATH


def _cli_invoker() -> Invoke:
    """Ejecutor en proceso sobre `pymedia.main.app` (rápido, depurable)."""
    runner = CliRunner(env={"COLUMNS": "300"})

    def invoke(*args: str, input: str | None = None) -> CliResult:
        result = runner.invoke(app, list(args), input=input)
        return CliResult(exit_code=result.exit_code, output=result.output)

    return invoke


def _binary_invoker(binary: Path, localedir: Path) -> Invoke:
    """Ejecutor que lanza el binario compilado como un proceso independiente."""
    # `COLUMNS` amplio: mismo motivo que en el CliRunner (Rich parte líneas).
    env = os.environ | {"PYMEDIA_LOCALEDIR": str(localedir), "COLUMNS": "300"}

    def invoke(*args: str, input: str | None = None) -> CliResult:
        result = subprocess.run(
            [str(binary), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
            input=input,
            check=False,
        )
        return CliResult(
            exit_code=result.returncode, output=result.stdout + result.stderr
        )

    return invoke


@pytest.fixture(params=["cli", pytest.param("binary", marks=pytest.mark.binary)])
def pymedia(request: pytest.FixtureRequest) -> Invoke:
    """Ejecuta pyMedia como CLI en proceso o como binario compilado.

    Cada test que use esta fixture se ejecuta dos veces (`[cli]` y `[binary]`);
    la variante `binary` se excluye por defecto con `-m 'not binary'`.
    """
    if request.param == "binary":
        return _binary_invoker(
            binary=request.getfixturevalue("built_binary"),
            localedir=request.getfixturevalue("empty_localedir"),
        )
    return _cli_invoker()
