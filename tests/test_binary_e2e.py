"""Tests end-to-end del binario PyInstaller de pyMedia.

Compila `build/pymedia.exe` con `scripts/build_windows.py` una única vez
por sesión y a continuación ejecuta el binario tal como lo haría un usuario
final, comprobando el código de salida, los mensajes visibles y las
propiedades de los ficheros generados (vía ffprobe). La superficie Typer
equivalente está cubierta por `tests/test_cli.py`.

El build tarda varios minutos: el módulo solo se ejecuta si se exporta
`PYMEDIA_BINARY_E2E=1`. P. ej.:

    PYMEDIA_BINARY_E2E=1 uv run pytest tests/test_binary_e2e.py -v
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest
from test_cli import (
    ffprobe_duration,
    ffprobe_streams,
    stream_codec_names,
    stream_tag,
    stream_types,
)

pytestmark = pytest.mark.prod

ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = ROOT / "scripts" / "build.py"
if sys.platform == "win32":
    binary_path = ROOT / "build" / "pymedia.exe"
else:
    binary_path = ROOT / "build" / "pymedia"


def run_binary(
    binary: Path,
    localedir: Path,
    *args: str,
) -> subprocess.CompletedProcess[str]:
    """Ejecuta el binario compilado con los argumentos indicados.

    Args:
        binary: Ruta del ejecutable compilado.
        localedir: Directorio de catálogos vacío que se inyecta como
            `PYMEDIA_LOCALEDIR` para que los msgid salgan en inglés
            independientemente del idioma del sistema o del config.toml.
        args: Argumentos de la CLI, sin el binario.

    Returns:
        Resultado del proceso con stdout/stderr capturados.
    """
    env = os.environ | {"PYMEDIA_LOCALEDIR": str(localedir)}
    return subprocess.run(
        [str(binary), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        check=False,
    )


def process_output(result: subprocess.CompletedProcess[str]) -> str:
    """Combina stdout y stderr para aserciones sobre mensajes visibles.

    Args:
        result: Resultado de `run_binary`.

    Returns:
        Salida completa del proceso, como la mezcla `CliRunner` de test_cli.
    """
    return result.stdout + result.stderr


@pytest.fixture(scope="session")
def empty_localedir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Directorio vacío que fuerza msgid en inglés dentro del binario."""
    return tmp_path_factory.mktemp("binary_empty_locales")


@pytest.fixture(scope="session")
def built_binary() -> Path:
    """Compila el ejecutable con el script oficial y devuelve su ruta.

    Returns:
        Ruta del `pymedia.exe` generado.

    Raises:
        Failed: Si el build de PyInstaller termina con error.
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
            f"build_windows.py falló (exit {result.returncode}):\n"
            f"{result.stdout}\n{result.stderr}"
        )
    assert binary_path.is_file(), f"No se generó {binary_path}"
    assert binary_path.stat().st_size > 1_000_000, "El ejecutable parece incompleto"
    return binary_path


# =============================================================================
#  build / help
# =============================================================================


def test_build_pyinstaller_produces_executable(built_binary: Path) -> None:
    """`scripts/build_windows.py` genera un ejecutable utilizable."""
    assert built_binary.is_file()
    assert built_binary.stat().st_size > 1_000_000


def test_binary_help_lists_commands(
    built_binary: Path,
    empty_localedir: Path,
) -> None:
    """`--help` termina sin error y lista los subcomandos principales."""
    result = run_binary(built_binary, empty_localedir, "--help")

    assert result.returncode == 0
    assert "Usage" in result.stdout
    for command in ("info", "remux", "transcode", "animated"):
        assert command in result.stdout


# =============================================================================
#  info
# =============================================================================


def test_info_success_shows_metadata(
    built_binary: Path,
    empty_localedir: Path,
    video_mp4_a: Path,
) -> None:
    """`info` termina sin error y muestra la tabla de metadatos del vídeo."""
    result = run_binary(built_binary, empty_localedir, "info", str(video_mp4_a))

    assert result.returncode == 0
    assert "Metadata" in result.stdout


def test_info_error_nonexistent_input(
    built_binary: Path,
    empty_localedir: Path,
    tmp_path: Path,
) -> None:
    """`info` con una ruta inexistente falla en la validación de Typer."""
    result = run_binary(
        built_binary,
        empty_localedir,
        "info",
        str(tmp_path / "missing.mp4"),
    )

    assert result.returncode != 0
    assert "is not a file" in process_output(result)


# =============================================================================
#  sheet
# =============================================================================


def test_sheet_success_generates_jpg(
    built_binary: Path,
    empty_localedir: Path,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`sheet --preset web` genera una imagen jpg con la rejilla de capturas."""
    output = tmp_path / "sheet.jpg"

    result = run_binary(
        built_binary,
        empty_localedir,
        "sheet",
        str(video_mp4_a),
        "-o",
        str(output),
        "--preset",
        "web",
    )

    assert result.returncode == 0
    assert output.exists()
    assert stream_codec_names(output, "video") == ["mjpeg"]


def test_sheet_error_exclusive_output_options(
    built_binary: Path,
    empty_localedir: Path,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`sheet` rechaza `--output` y `--directory` usados a la vez."""
    result = run_binary(
        built_binary,
        empty_localedir,
        "sheet",
        str(video_mp4_a),
        "-o",
        str(tmp_path / "sheet.jpg"),
        "-d",
        str(tmp_path),
    )

    assert result.returncode != 0
    assert "mutually exclusive" in process_output(result)


# =============================================================================
#  join
# =============================================================================


def test_join_success_concatenates_videos(
    built_binary: Path,
    empty_localedir: Path,
    video_mp4_a: Path,
    video_mp4_b: Path,
    tmp_path: Path,
) -> None:
    """`join` une dos vídeos en un contenedor con la duración combinada."""
    output = tmp_path / "joined.mp4"

    result = run_binary(
        built_binary,
        empty_localedir,
        "join",
        str(video_mp4_a),
        str(video_mp4_b),
        "-o",
        str(output),
        "-ov",
        "yes",
    )

    assert result.returncode == 0
    assert ffprobe_duration(output) >= 3.5


def test_join_error_single_input(
    built_binary: Path,
    empty_localedir: Path,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`join` con un único vídeo exige al menos dos entradas."""
    result = run_binary(
        built_binary,
        empty_localedir,
        "join",
        str(video_mp4_a),
        "-o",
        str(tmp_path / "joined.mp4"),
    )

    assert result.returncode != 0
    assert "at least 2 videos" in process_output(result)


# =============================================================================
#  remux
# =============================================================================


def test_remux_success_changes_container(
    built_binary: Path,
    empty_localedir: Path,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`remux` copia los streams a un contenedor distinto sin recodificar."""
    output = tmp_path / "remuxed.mkv"

    result = run_binary(
        built_binary,
        empty_localedir,
        "remux",
        str(video_mp4_a),
        "-o",
        str(output),
        "-ov",
        "yes",
    )

    assert result.returncode == 0
    assert output.exists()
    assert stream_types(output) == ["video", "audio"]


def test_remux_error_fast_start_non_mp4(
    built_binary: Path,
    empty_localedir: Path,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`remux` rechaza `--fast-start` con un contenedor distinto de mp4."""
    result = run_binary(
        built_binary,
        empty_localedir,
        "remux",
        str(video_mp4_a),
        "-o",
        str(tmp_path / "remuxed.mkv"),
        "--fast-start",
    )

    assert result.returncode != 0
    assert "Fast start only works" in process_output(result)


# =============================================================================
#  cut
# =============================================================================


def test_cut_success_cuts_at_timestamp(
    built_binary: Path,
    empty_localedir: Path,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`cut --at` divide el vídeo en un segmento por cada marca."""
    output = tmp_path / "part.mp4"

    result = run_binary(
        built_binary,
        empty_localedir,
        "cut",
        str(video_mp4_a),
        "--at",
        "00:00:01",
        "-o",
        str(output),
        "-ov",
        "yes",
    )

    assert result.returncode == 0
    parts = sorted(tmp_path.glob("part_*.mp4"))
    assert len(parts) == 2
    assert all(ffprobe_duration(part) < 1.9 for part in parts)


def test_cut_error_missing_options(
    built_binary: Path,
    empty_localedir: Path,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`cut` exige una de `--at`, `--start` o `--end`."""
    result = run_binary(
        built_binary,
        empty_localedir,
        "cut",
        str(video_mp4_a),
        "-o",
        str(tmp_path / "part.mp4"),
    )

    assert result.returncode != 0
    assert "Missing required options: at, start, end" in process_output(result)


# =============================================================================
#  transcode
# =============================================================================


def test_transcode_success_transcodes_video(
    built_binary: Path,
    empty_localedir: Path,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`transcode --video` recodifica la pista con el preset por defecto."""
    output = tmp_path / "transcoded.mp4"

    result = run_binary(
        built_binary,
        empty_localedir,
        "transcode",
        str(video_mp4_a),
        "--video",
        "-o",
        str(output),
        "-ov",
        "yes",
    )

    assert result.returncode == 0
    assert stream_codec_names(output, "video") == ["hevc"]


def test_transcode_error_missing_action(
    built_binary: Path,
    empty_localedir: Path,
    video_mp4_a: Path,
) -> None:
    """`transcode` sin ninguna opción de transcodificación avisa de las requeridas."""
    result = run_binary(built_binary, empty_localedir, "transcode", str(video_mp4_a))

    assert result.returncode != 0
    normalized = " ".join(process_output(result).split())
    assert "Missing required options:" in normalized
    for option in (
        "audio",
        "video",
        "burn-subtitles",
        "crop",
        "rotate",
        "scale_to",
        "hflip",
        "vflip",
    ):
        assert option in normalized


# =============================================================================
#  add-audio
# =============================================================================


def test_add_audio_success_inserts_track(
    built_binary: Path,
    empty_localedir: Path,
    video_mkv: Path,
    audio_m4a: Path,
    tmp_path: Path,
) -> None:
    """`add-audio` añade la pista externa con su idioma al contenedor."""
    output = tmp_path / "with_audio.mkv"

    result = run_binary(
        built_binary,
        empty_localedir,
        "add-audio",
        str(video_mkv),
        str(audio_m4a),
        "--language",
        "eng",
        "-o",
        str(output),
        "-ov",
        "yes",
    )

    assert result.returncode == 0
    audio_streams = [
        stream
        for stream in ffprobe_streams(output)
        if stream.get("codec_type") == "audio"
    ]
    assert len(audio_streams) == 2
    assert (audio_streams[1].get("tags") or {}).get("language") == "eng"


def test_add_audio_error_missing_language(
    built_binary: Path,
    empty_localedir: Path,
    video_mkv: Path,
    audio_m4a: Path,
    tmp_path: Path,
) -> None:
    """`add-audio` exige la opción `--language` para la nueva pista."""
    result = run_binary(
        built_binary,
        empty_localedir,
        "add-audio",
        str(video_mkv),
        str(audio_m4a),
        "-o",
        str(tmp_path / "with_audio.mkv"),
    )

    assert result.returncode != 0
    assert "Missing option '--language'" in process_output(result)


# =============================================================================
#  delete-audio
# =============================================================================


def test_delete_audio_success_removes_tracks(
    built_binary: Path,
    empty_localedir: Path,
    video_mkv: Path,
    tmp_path: Path,
) -> None:
    """`delete-audio` elimina las pistas indicadas del contenedor."""
    output = tmp_path / "no_audio.mkv"

    result = run_binary(
        built_binary,
        empty_localedir,
        "delete-audio",
        str(video_mkv),
        "--tracks",
        "0",
        "-o",
        str(output),
        "-ov",
        "yes",
    )

    assert result.returncode == 0
    assert "audio" not in stream_types(output)


def test_delete_audio_error_without_audio_tracks(
    built_binary: Path,
    empty_localedir: Path,
    video_no_audio: Path,
    tmp_path: Path,
) -> None:
    """`delete-audio` avisa cuando el medio no tiene pistas de audio."""
    result = run_binary(
        built_binary,
        empty_localedir,
        "delete-audio",
        str(video_no_audio),
        "--tracks",
        "0",
        "-o",
        str(tmp_path / "out.mp4"),
        "-ov",
        "yes",
    )

    assert result.returncode != 0
    assert "Missing parameter: media.audio" in process_output(result)


# =============================================================================
#  edit-audio
# =============================================================================


def test_edit_audio_success_updates_metadata(
    built_binary: Path,
    empty_localedir: Path,
    video_mkv: Path,
    tmp_path: Path,
) -> None:
    """`edit-audio` actualiza el idioma y el título de la pista indicada."""
    output = tmp_path / "edited_audio.mkv"

    result = run_binary(
        built_binary,
        empty_localedir,
        "edit-audio",
        str(video_mkv),
        "--track",
        "0",
        "--language",
        "fre",
        "--title",
        "Edited",
        "-o",
        str(output),
        "-ov",
        "yes",
    )

    assert result.returncode == 0
    assert stream_tag(output, "audio", "language") == "fre"
    assert stream_tag(output, "audio", "title") == "Edited"


def test_edit_audio_error_missing_track(
    built_binary: Path,
    empty_localedir: Path,
    video_mkv: Path,
) -> None:
    """`edit-audio` exige la opción `--track` para identificar la pista."""
    result = run_binary(
        built_binary,
        empty_localedir,
        "edit-audio",
        str(video_mkv),
        "--language",
        "fre",
    )

    assert result.returncode != 0
    assert "Missing option '--track'" in process_output(result)


# =============================================================================
#  extract-audio
# =============================================================================


def test_extract_audio_success_extracts_track(
    built_binary: Path,
    empty_localedir: Path,
    video_mkv: Path,
    tmp_path: Path,
) -> None:
    """`extract-audio` vuelca la pista indicada a un fichero de audio."""
    output = tmp_path / "audio.m4a"

    result = run_binary(
        built_binary,
        empty_localedir,
        "extract-audio",
        str(video_mkv),
        "--tracks",
        "0",
        "-o",
        str(output),
        "-ov",
        "yes",
    )

    assert result.returncode == 0
    extracted = list(tmp_path.glob("audio_audio_track_*.m4a"))
    assert len(extracted) == 1
    assert "audio" in stream_types(extracted[0])


def test_extract_audio_error_without_audio_tracks(
    built_binary: Path,
    empty_localedir: Path,
    video_no_audio: Path,
) -> None:
    """`extract-audio` avisa cuando el medio no tiene pistas de audio."""
    result = run_binary(
        built_binary,
        empty_localedir,
        "extract-audio",
        str(video_no_audio),
        "--tracks",
        "0",
    )

    assert result.returncode != 0
    assert "Missing parameter: media.audio" in process_output(result)


# =============================================================================
#  add-subs
# =============================================================================


def test_add_subs_success_inserts_track(
    built_binary: Path,
    empty_localedir: Path,
    video_mkv: Path,
    subs_spa: Path,
    tmp_path: Path,
) -> None:
    """`add-subs` inserta el fichero externo como pista con su idioma."""
    output = tmp_path / "with_subs.mkv"

    result = run_binary(
        built_binary,
        empty_localedir,
        "add-subs",
        str(video_mkv),
        str(subs_spa),
        "--language",
        "spa",
        "-o",
        str(output),
        "-ov",
        "yes",
    )

    assert result.returncode == 0
    sub_streams = [
        stream
        for stream in ffprobe_streams(output)
        if stream.get("codec_type") == "subtitle"
    ]
    assert len(sub_streams) == 1
    assert (sub_streams[0].get("tags") or {}).get("language") == "spa"


def test_add_subs_error_invalid_subtitles_file(
    built_binary: Path,
    empty_localedir: Path,
    video_mkv: Path,
    subs_bad: Path,
    tmp_path: Path,
) -> None:
    """`add-subs` rechaza ficheros con extensión srt pero contenido inválido."""
    result = run_binary(
        built_binary,
        empty_localedir,
        "add-subs",
        str(video_mkv),
        str(subs_bad),
        "--language",
        "spa",
        "-o",
        str(tmp_path / "with_subs.mkv"),
        "-ov",
        "yes",
    )

    assert result.returncode != 0
    assert "Invalid data found" in process_output(result)


# =============================================================================
#  delete-subs
# =============================================================================


def test_delete_subs_success_removes_track(
    built_binary: Path,
    empty_localedir: Path,
    video_mkv_subs: Path,
    tmp_path: Path,
) -> None:
    """`delete-subs` elimina las pistas indicadas y conserva el resto."""
    output = tmp_path / "fewer_subs.mkv"

    result = run_binary(
        built_binary,
        empty_localedir,
        "delete-subs",
        str(video_mkv_subs),
        "--tracks",
        "1",
        "-o",
        str(output),
        "-ov",
        "yes",
    )

    assert result.returncode == 0
    languages = [
        (stream.get("tags") or {}).get("language")
        for stream in ffprobe_streams(output)
        if stream.get("codec_type") == "subtitle"
    ]
    assert languages == ["spa"]


def test_delete_subs_error_without_subtitles(
    built_binary: Path,
    empty_localedir: Path,
    video_mkv: Path,
    tmp_path: Path,
) -> None:
    """`delete-subs` avisa cuando el medio no tiene pistas de subtítulos."""
    result = run_binary(
        built_binary,
        empty_localedir,
        "delete-subs",
        str(video_mkv),
        "--tracks",
        "0",
        "-o",
        str(tmp_path / "out.mkv"),
        "-ov",
        "yes",
    )

    assert result.returncode != 0
    assert "Missing parameter: media.subtitles" in process_output(result)


# =============================================================================
#  edit-subs
# =============================================================================


def test_edit_subs_success_updates_metadata(
    built_binary: Path,
    empty_localedir: Path,
    video_mkv_subs: Path,
    tmp_path: Path,
) -> None:
    """`edit-subs` actualiza el idioma de la pista de subtítulos indicada."""
    output = tmp_path / "edited_subs.mkv"

    result = run_binary(
        built_binary,
        empty_localedir,
        "edit-subs",
        str(video_mkv_subs),
        "--track",
        "0",
        "--language",
        "fre",
        "-o",
        str(output),
        "-ov",
        "yes",
    )

    assert result.returncode == 0
    assert stream_tag(output, "subtitle", "language") == "fre"


def test_edit_subs_error_missing_track(
    built_binary: Path,
    empty_localedir: Path,
    video_mkv_subs: Path,
) -> None:
    """`edit-subs` exige la opción `--track` para identificar la pista."""
    result = run_binary(
        built_binary,
        empty_localedir,
        "edit-subs",
        str(video_mkv_subs),
        "--language",
        "fre",
    )

    assert result.returncode != 0
    assert "Missing option '--track'" in process_output(result)


# =============================================================================
#  extract-subs
# =============================================================================


def test_extract_subs_success_extracts_track(
    built_binary: Path,
    empty_localedir: Path,
    video_mkv_subs: Path,
    tmp_path: Path,
) -> None:
    """`extract-subs` vuelca la pista indicada a un fichero srt."""
    output = tmp_path / "subs.srt"

    result = run_binary(
        built_binary,
        empty_localedir,
        "extract-subs",
        str(video_mkv_subs),
        "--tracks",
        "0",
        "-o",
        str(output),
        "-ov",
        "yes",
    )

    assert result.returncode == 0
    extracted = list(tmp_path.glob("subs_subtitles_track_*.srt"))
    assert len(extracted) == 1
    assert "Hola prueba" in extracted[0].read_text(encoding="utf-8")


def test_extract_subs_error_incompatible_container(
    built_binary: Path,
    empty_localedir: Path,
    video_mkv_subs: Path,
    tmp_path: Path,
) -> None:
    """`extract-subs` rechaza contenedores no compatibles con el códec srt."""
    result = run_binary(
        built_binary,
        empty_localedir,
        "extract-subs",
        str(video_mkv_subs),
        "--tracks",
        "0",
        "-o",
        str(tmp_path / "subs.ass"),
        "-ov",
        "yes",
    )

    assert result.returncode != 0
    assert "srt" in process_output(result)


# =============================================================================
#  animated
# =============================================================================


def test_animated_success_generates_gif(
    built_binary: Path,
    empty_localedir: Path,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`animated --end` genera un gif limitado al rango temporal indicado."""
    output = tmp_path / "anim.gif"

    result = run_binary(
        built_binary,
        empty_localedir,
        "animated",
        str(video_mp4_a),
        "-o",
        str(output),
        "-ov",
        "yes",
        "--fps",
        "10",
        "--end",
        "00:00:01",
    )

    assert result.returncode == 0
    assert output.exists()
    assert stream_codec_names(output, "video") == ["gif"]


def test_animated_error_invalid_container(
    built_binary: Path,
    empty_localedir: Path,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`animated` rechaza salidas que no sean imágenes animadas."""
    result = run_binary(
        built_binary,
        empty_localedir,
        "animated",
        str(video_mp4_a),
        "-o",
        str(tmp_path / "anim.mp4"),
        "-ov",
        "yes",
    )

    assert result.returncode != 0
    assert "Invalid extension .mp4" in process_output(result)


# =============================================================================
#  frames
# =============================================================================


def test_frames_success_captures_at_timestamp(
    built_binary: Path,
    empty_localedir: Path,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`frames --at` captura una miniatura en cada marca indicada."""
    output = tmp_path / "thumb.jpg"

    result = run_binary(
        built_binary,
        empty_localedir,
        "frames",
        str(video_mp4_a),
        "--at",
        "00:00:01",
        "-o",
        str(output),
        "-ov",
        "yes",
    )

    assert result.returncode == 0
    assert len(list(tmp_path.glob("thumb_*.jpg"))) == 1


def test_frames_error_invalid_timestamp(
    built_binary: Path,
    empty_localedir: Path,
    video_mp4_a: Path,
) -> None:
    """`frames` rechaza marcas de tiempo con formato distinto de hh:mm:ss."""
    result = run_binary(
        built_binary,
        empty_localedir,
        "frames",
        str(video_mp4_a),
        "--at",
        "zz:zz",
    )

    assert result.returncode != 0
    assert "Invalid timestamp format" in process_output(result)


# =============================================================================
#  interval
# =============================================================================


def test_interval_success_generates_series(
    built_binary: Path,
    empty_localedir: Path,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`interval --every` genera miniaturas periódicas numeradas."""
    output = tmp_path / "periodic.jpg"

    result = run_binary(
        built_binary,
        empty_localedir,
        "interval",
        str(video_mp4_a),
        "--every",
        "1",
        "-o",
        str(output),
        "-ov",
        "yes",
    )

    assert result.returncode == 0
    assert len(list(tmp_path.glob("periodic_*.jpg"))) >= 1


def test_interval_error_missing_every(
    built_binary: Path,
    empty_localedir: Path,
    video_mp4_a: Path,
) -> None:
    """`interval` exige la opción `--every` para calcular el periodo."""
    result = run_binary(built_binary, empty_localedir, "interval", str(video_mp4_a))

    assert result.returncode != 0
    assert "Missing parameter: fps" in process_output(result)


# =============================================================================
#  scene
# =============================================================================


def test_scene_success_detects_scene_changes(
    built_binary: Path,
    empty_localedir: Path,
    video_scenes: Path,
    tmp_path: Path,
) -> None:
    """`scene --scene` captura una miniatura en cada corte detectado."""
    output = tmp_path / "scene.jpg"

    result = run_binary(
        built_binary,
        empty_localedir,
        "scene",
        str(video_scenes),
        "--scene",
        "0.3",
        "-o",
        str(output),
        "-ov",
        "yes",
    )

    assert result.returncode == 0
    assert len(list(tmp_path.glob("scene_*.jpg"))) == 2


def test_scene_error_threshold_out_of_range(
    built_binary: Path,
    empty_localedir: Path,
    video_scenes: Path,
) -> None:
    """`scene` valida que el umbral esté en el rango permitido por Typer."""
    result = run_binary(
        built_binary,
        empty_localedir,
        "scene",
        str(video_scenes),
        "--scene",
        "5",
    )

    assert result.returncode != 0
    assert "Invalid value for '--scene'" in process_output(result)
