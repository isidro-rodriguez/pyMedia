"""Regresiones de errores detectados en la revisión de Linux.

Usan la fixture `pymedia`: cada regresión se comprueba como CLI y como binario.
"""

from pathlib import Path

from helpers import Invoke, stream_types


def test_remux_same_input_output_keeps_source(
    pymedia: Invoke, tmp_path: Path, video_mp4_a: Path
) -> None:
    """Una salida igual a la entrada se rechaza y no borra el original."""
    source = tmp_path / "src.mp4"
    source.write_bytes(video_mp4_a.read_bytes())

    result = pymedia("remux", str(source), "-o", str(source), "-ov", "yes")

    assert result.exit_code != 0
    assert "must be different" in result.output
    assert source.exists()


def test_transcode_keeps_subtitles_and_stream_order(
    pymedia: Invoke, tmp_path: Path, video_mkv_subs: Path
) -> None:
    """`transcode` conserva los subtítulos y deja el vídeo en primer lugar."""
    output = tmp_path / "out.mkv"

    result = pymedia(
        "transcode", str(video_mkv_subs), "--video", "-o", str(output), "-ov", "yes"
    )

    assert result.exit_code == 0
    types = stream_types(output)
    assert types[0] == "video"
    assert "subtitle" in types
    assert types == stream_types(video_mkv_subs)


def test_join_keeps_all_tracks(
    pymedia: Invoke, tmp_path: Path, video_mkv_subs: Path
) -> None:
    """`join` copia todas las pistas, no solo el primer vídeo y audio."""
    output = tmp_path / "joined.mkv"

    result = pymedia(
        "join",
        str(video_mkv_subs),
        str(video_mkv_subs),
        "-o",
        str(output),
        "-ov",
        "yes",
    )

    assert result.exit_code == 0
    assert stream_types(output) == stream_types(video_mkv_subs)


def test_frames_overwrite_no_does_not_hang(
    pymedia: Invoke, tmp_path: Path, video_mp4_a: Path
) -> None:
    """`--overwrite no` omite la captura existente en vez de esperar a ffmpeg."""
    out = tmp_path / "f.jpg"
    args = ["frames", str(video_mp4_a), "--at", "00:01", "-o", str(out)]
    assert pymedia(*args, "-ov", "yes").exit_code == 0
    captured = tmp_path / "f_0-00-01.jpg"
    assert captured.exists()
    before = captured.stat().st_mtime_ns

    result = pymedia(*args, "-ov", "no")

    assert result.exit_code == 0
    assert captured.stat().st_mtime_ns == before


def test_scene_default_sensitivity(
    pymedia: Invoke, tmp_path: Path, video_scenes: Path
) -> None:
    """`scene` sin `--scene` usa la sensibilidad por defecto."""
    result = pymedia(
        "scene", str(video_scenes), "-o", str(tmp_path / "s.jpg"), "-ov", "yes"
    )

    assert result.exit_code == 0


def test_interval_zero_is_user_error(pymedia: Invoke, video_mp4_a: Path) -> None:
    """`--every 0` da un error de usuario, no un ZeroDivisionError."""
    result = pymedia("interval", str(video_mp4_a), "--every", "0")

    assert result.exit_code != 0
    assert "at least 1 second" in result.output


def test_frames_requires_at(pymedia: Invoke, video_mp4_a: Path) -> None:
    """`frames` sin `--at` pide la opción en lugar de fallar con traceback."""
    result = pymedia("frames", str(video_mp4_a))

    assert result.exit_code != 0
    assert "Missing required option: at" in result.output


def test_scene_ask_detects_existing_files(
    pymedia: Invoke, tmp_path: Path, video_scenes: Path
) -> None:
    """Con `--overwrite ask`, `scene` pregunta si ya hay capturas numeradas."""
    out = tmp_path / "s.jpg"
    args = ["scene", str(video_scenes), "-o", str(out)]
    assert pymedia(*args, "-ov", "yes").exit_code == 0
    first = tmp_path / "s_001.jpg"
    assert first.exists()
    before = first.stat().st_mtime_ns

    result = pymedia(*args, "-ov", "ask", input="n\n")

    assert "Overwrite?" in result.output
    assert first.stat().st_mtime_ns == before
