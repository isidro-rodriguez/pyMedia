"""Tests end-to-end de la superficie Typer de la CLI de pyMedia.

Cada test invoca `pymedia.main.app` con `typer.testing.CliRunner` tal como lo
haría un usuario, comprobando el código de salida, los mensajes visibles y las
propiedades básicas de los ficheros generados (vía ffprobe). La lógica interna
de mixins y pipelines ya está cubierta por el resto de suites.
"""

import json
import subprocess
from pathlib import Path
from typing import Any, cast

from typer.testing import CliRunner

from pymedia.main import app


def ffprobe_streams(path: Path) -> list[dict[str, Any]]:
    """Devuelve los streams que ffprobe detecta en el fichero indicado.

    Args:
        path: Ruta del fichero multimedia a inspeccionar.

    Returns:
        Streams del fichero en formato JSON de ffprobe.
    """
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_streams",
            str(path),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    data = cast(dict[str, Any], json.loads(result.stdout))
    return cast(list[dict[str, Any]], data["streams"])


def ffprobe_duration(path: Path) -> float:
    """Devuelve la duración total, en segundos, del fichero indicado.

    Args:
        path: Ruta del fichero multimedia a inspeccionar.

    Returns:
        Duración total del fichero en segundos.
    """
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            str(path),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    data = cast(dict[str, Any], json.loads(result.stdout))
    return float(data["format"]["duration"])


def stream_types(path: Path) -> list[str | None]:
    """Lista los tipos de stream (video/audio/subtitle) del fichero indicado.

    Args:
        path: Ruta del fichero multimedia a inspeccionar.

    Returns:
        Tipos de stream en el orden que reporta ffprobe.
    """
    return [stream.get("codec_type") for stream in ffprobe_streams(path)]


def stream_tag(path: Path, stream_type: str, tag: str, index: int = 0) -> str | None:
    """Devuelve un tag del stream indicado según su tipo y posición local.

    Args:
        path: Ruta del fichero multimedia a inspeccionar.
        stream_type: Tipo de stream (video/audio/subtitle).
        tag: Nombre del tag (p. ej. `language` o `title`).
        index: Índice local dentro del tipo de stream.

    Returns:
        Valor del tag, o `None` si no está presente.
    """
    matching = [
        stream
        for stream in ffprobe_streams(path)
        if stream.get("codec_type") == stream_type
    ]
    tags = matching[index].get("tags") or {}
    return tags.get(tag)


def stream_codec_names(path: Path, stream_type: str) -> list[str | None]:
    """Lista los códecs de los streams del tipo indicado.

    Args:
        path: Ruta del fichero multimedia a inspeccionar.
        stream_type: Tipo de stream (video/audio/subtitle).

    Returns:
        Nombres de códec en el orden que reporta ffprobe.
    """
    return [
        stream.get("codec_name")
        for stream in ffprobe_streams(path)
        if stream.get("codec_type") == stream_type
    ]


# =============================================================================
#  info
# =============================================================================


def test_info_success_shows_metadata(runner: CliRunner, video_mp4_a: Path) -> None:
    """`info` termina sin error y muestra la tabla de metadatos del vídeo."""
    result = runner.invoke(app, ["info", str(video_mp4_a)])

    assert result.exit_code == 0
    assert "Metadata" in result.output


def test_info_error_nonexistent_input(runner: CliRunner, tmp_path: Path) -> None:
    """`info` con una ruta inexistente falla en la validación de Typer."""
    result = runner.invoke(app, ["info", str(tmp_path / "missing.mp4")])

    assert result.exit_code != 0
    assert "is not a file" in result.output


# =============================================================================
#  sheet
# =============================================================================


def test_sheet_success_generates_jpg(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`sheet --preset web` genera una imagen jpg con la rejilla de capturas."""
    output = tmp_path / "sheet.jpg"

    result = runner.invoke(
        app,
        ["sheet", str(video_mp4_a), "-o", str(output), "--preset", "web"],
    )

    assert result.exit_code == 0
    assert output.exists()
    assert stream_codec_names(output, "video") == ["mjpeg"]


def test_sheet_error_exclusive_output_options(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`sheet` rechaza `--output` y `--directory` usados a la vez."""
    result = runner.invoke(
        app,
        [
            "sheet",
            str(video_mp4_a),
            "-o",
            str(tmp_path / "sheet.jpg"),
            "-d",
            str(tmp_path),
        ],
    )

    assert result.exit_code != 0
    assert "mutually exclusive" in result.output


# =============================================================================
#  join
# =============================================================================


def test_join_success_concatenates_videos(
    runner: CliRunner,
    video_mp4_a: Path,
    video_mp4_b: Path,
    tmp_path: Path,
) -> None:
    """`join` une dos vídeos en un contenedor con la duración combinada."""
    output = tmp_path / "joined.mp4"

    result = runner.invoke(
        app,
        ["join", str(video_mp4_a), str(video_mp4_b), "-o", str(output), "-ov", "yes"],
    )

    assert result.exit_code == 0
    assert ffprobe_duration(output) >= 3.5


def test_join_error_single_input(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`join` con un único vídeo exige al menos dos entradas."""
    result = runner.invoke(
        app,
        ["join", str(video_mp4_a), "-o", str(tmp_path / "joined.mp4")],
    )

    assert result.exit_code != 0
    assert "at least 2 videos" in result.output


# =============================================================================
#  remux
# =============================================================================


def test_remux_success_changes_container(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`remux` copia los streams a un contenedor distinto sin recodificar."""
    output = tmp_path / "remuxed.mkv"

    result = runner.invoke(
        app,
        ["remux", str(video_mp4_a), "-o", str(output), "-ov", "yes"],
    )

    assert result.exit_code == 0
    assert output.exists()
    assert stream_types(output) == ["video", "audio"]


def test_remux_error_fast_start_non_mp4(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`remux` rechaza `--fast-start` con un contenedor distinto de mp4."""
    result = runner.invoke(
        app,
        [
            "remux",
            str(video_mp4_a),
            "-o",
            str(tmp_path / "remuxed.mkv"),
            "--fast-start",
        ],
    )

    assert result.exit_code != 0
    assert "Fast start only works" in result.output


# =============================================================================
#  split
# =============================================================================


def test_split_success_cuts_at_timestamp(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`split --at` divide el vídeo en un segmento por cada marca."""
    output = tmp_path / "part.mp4"

    result = runner.invoke(
        app,
        [
            "split",
            str(video_mp4_a),
            "--at",
            "00:00:01",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    parts = sorted(tmp_path.glob("part_*.mp4"))
    assert len(parts) == 2
    assert all(ffprobe_duration(part) < 1.9 for part in parts)


def test_split_error_missing_at(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`split` exige la opción `--at` con las marcas de tiempo."""
    result = runner.invoke(
        app,
        ["split", str(video_mp4_a), "-o", str(tmp_path / "part.mp4")],
    )

    assert result.exit_code != 0
    assert "Missing option '--at'" in result.output


# =============================================================================
#  transcode
# =============================================================================


def test_transcode_success_transcodes_video(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`transcode --video` recodifica la pista con el preset por defecto."""
    output = tmp_path / "transcoded.mp4"

    result = runner.invoke(
        app,
        ["transcode", str(video_mp4_a), "--video", "-o", str(output), "-ov", "yes"],
    )

    assert result.exit_code == 0
    assert stream_codec_names(output, "video") == ["hevc"]


def test_transcode_success_burns_subtitles(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`transcode --burn-subtitles` quema el fichero srt indicado en el vídeo."""
    subtitle = tmp_path / "eng_subs.srt"
    subtitle.write_text(
        "1\n00:00:00,000 --> 00:00:02,000\nHello test\n", encoding="utf-8"
    )
    output = tmp_path / "burned.mp4"

    result = runner.invoke(
        app,
        [
            "transcode",
            str(video_mp4_a),
            "--burn-subtitles",
            str(subtitle),
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    assert output.exists()


def test_transcode_error_missing_action(
    runner: CliRunner,
    video_mp4_a: Path,
) -> None:
    """`transcode` sin ninguna opción de transcodificación avisa de las requeridas."""
    result = runner.invoke(app, ["transcode", str(video_mp4_a)])

    assert result.exit_code != 0
    assert "One of the following options is required" in result.output


# =============================================================================
#  add-audio
# =============================================================================


def test_add_audio_success_inserts_track(
    runner: CliRunner,
    video_mkv: Path,
    audio_m4a: Path,
    tmp_path: Path,
) -> None:
    """`add-audio` añade la pista externa con su idioma al contenedor."""
    output = tmp_path / "with_audio.mkv"

    result = runner.invoke(
        app,
        [
            "add-audio",
            str(video_mkv),
            str(audio_m4a),
            "--language",
            "eng",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    audio_streams = [
        stream
        for stream in ffprobe_streams(output)
        if stream.get("codec_type") == "audio"
    ]
    assert len(audio_streams) == 2
    assert (audio_streams[1].get("tags") or {}).get("language") == "eng"


def test_add_audio_error_missing_language(
    runner: CliRunner,
    video_mkv: Path,
    audio_m4a: Path,
    tmp_path: Path,
) -> None:
    """`add-audio` exige la opción `--language` para la nueva pista."""
    result = runner.invoke(
        app,
        [
            "add-audio",
            str(video_mkv),
            str(audio_m4a),
            "-o",
            str(tmp_path / "with_audio.mkv"),
        ],
    )

    assert result.exit_code != 0
    assert "Missing option '--language'" in result.output


# =============================================================================
#  delete-audio
# =============================================================================


def test_delete_audio_success_removes_tracks(
    runner: CliRunner,
    video_mkv: Path,
    tmp_path: Path,
) -> None:
    """`delete-audio` elimina las pistas indicadas del contenedor."""
    output = tmp_path / "no_audio.mkv"

    result = runner.invoke(
        app,
        [
            "delete-audio",
            str(video_mkv),
            "--tracks",
            "0",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    assert "audio" not in stream_types(output)


def test_delete_audio_error_without_audio_tracks(
    runner: CliRunner,
    video_no_audio: Path,
    tmp_path: Path,
) -> None:
    """`delete-audio` avisa cuando el medio no tiene pistas de audio."""
    result = runner.invoke(
        app,
        [
            "delete-audio",
            str(video_no_audio),
            "-o",
            str(tmp_path / "out.mp4"),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code != 0
    assert "Missing parameter: audio" in result.output


# =============================================================================
#  edit-audio
# =============================================================================


def test_edit_audio_success_updates_metadata(
    runner: CliRunner,
    video_mkv: Path,
    tmp_path: Path,
) -> None:
    """`edit-audio` actualiza el idioma y el título de la pista indicada."""
    output = tmp_path / "edited_audio.mkv"

    result = runner.invoke(
        app,
        [
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
        ],
    )

    assert result.exit_code == 0
    assert stream_tag(output, "audio", "language") == "fre"
    assert stream_tag(output, "audio", "title") == "Edited"


def test_edit_audio_error_missing_track(
    runner: CliRunner,
    video_mkv: Path,
) -> None:
    """`edit-audio` exige la opción `--track` para identificar la pista."""
    result = runner.invoke(
        app,
        ["edit-audio", str(video_mkv), "--language", "fre"],
    )

    assert result.exit_code != 0
    assert "Missing option '--track'" in result.output


# =============================================================================
#  extract-audio
# =============================================================================


def test_extract_audio_success_extracts_track(
    runner: CliRunner,
    video_mkv: Path,
    tmp_path: Path,
) -> None:
    """`extract-audio` vuelca la pista indicada a un fichero de audio."""
    output = tmp_path / "audio.m4a"

    result = runner.invoke(
        app,
        [
            "extract-audio",
            str(video_mkv),
            "--tracks",
            "0",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    extracted = list(tmp_path.glob("audio_audio_track_*.m4a"))
    assert len(extracted) == 1
    assert "audio" in stream_types(extracted[0])


def test_extract_audio_error_without_audio_tracks(
    runner: CliRunner,
    video_no_audio: Path,
) -> None:
    """`extract-audio` avisa cuando el medio no tiene pistas de audio."""
    result = runner.invoke(app, ["extract-audio", str(video_no_audio)])

    assert result.exit_code != 0
    assert "Missing parameter: audio" in result.output


# =============================================================================
#  add-subs
# =============================================================================


def test_add_subs_success_inserts_track(
    runner: CliRunner,
    video_mkv: Path,
    subs_spa: Path,
    tmp_path: Path,
) -> None:
    """`add-subs` inserta el fichero externo como pista con su idioma."""
    output = tmp_path / "with_subs.mkv"

    result = runner.invoke(
        app,
        [
            "add-subs",
            str(video_mkv),
            str(subs_spa),
            "--language",
            "spa",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    sub_streams = [
        stream
        for stream in ffprobe_streams(output)
        if stream.get("codec_type") == "subtitle"
    ]
    assert len(sub_streams) == 1
    assert (sub_streams[0].get("tags") or {}).get("language") == "spa"


def test_add_subs_error_invalid_subtitles_file(
    runner: CliRunner,
    video_mkv: Path,
    subs_bad: Path,
    tmp_path: Path,
) -> None:
    """`add-subs` rechaza ficheros con extensión srt pero contenido inválido."""
    result = runner.invoke(
        app,
        [
            "add-subs",
            str(video_mkv),
            str(subs_bad),
            "--language",
            "spa",
            "-o",
            str(tmp_path / "with_subs.mkv"),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code != 0
    assert "Invalid data found" in result.output


# =============================================================================
#  delete-subs
# =============================================================================


def test_delete_subs_success_removes_track(
    runner: CliRunner,
    video_mkv_subs: Path,
    tmp_path: Path,
) -> None:
    """`delete-subs` elimina las pistas indicadas y conserva el resto."""
    output = tmp_path / "fewer_subs.mkv"

    result = runner.invoke(
        app,
        [
            "delete-subs",
            str(video_mkv_subs),
            "--tracks",
            "1",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    languages = [
        (stream.get("tags") or {}).get("language")
        for stream in ffprobe_streams(output)
        if stream.get("codec_type") == "subtitle"
    ]
    assert languages == ["spa"]


def test_delete_subs_error_without_subtitles(
    runner: CliRunner,
    video_mkv: Path,
    tmp_path: Path,
) -> None:
    """`delete-subs` avisa cuando el medio no tiene pistas de subtítulos."""
    result = runner.invoke(
        app,
        ["delete-subs", str(video_mkv), "-o", str(tmp_path / "out.mkv"), "-ov", "yes"],
    )

    assert result.exit_code != 0
    assert "does not contain subtitles streams" in result.output


# =============================================================================
#  edit-subs
# =============================================================================


def test_edit_subs_success_updates_metadata(
    runner: CliRunner,
    video_mkv_subs: Path,
    tmp_path: Path,
) -> None:
    """`edit-subs` actualiza el idioma de la pista de subtítulos indicada."""
    output = tmp_path / "edited_subs.mkv"

    result = runner.invoke(
        app,
        [
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
        ],
    )

    assert result.exit_code == 0
    assert stream_tag(output, "subtitle", "language") == "fre"


def test_edit_subs_error_missing_track(
    runner: CliRunner,
    video_mkv_subs: Path,
) -> None:
    """`edit-subs` exige la opción `--track` para identificar la pista."""
    result = runner.invoke(
        app,
        ["edit-subs", str(video_mkv_subs), "--language", "fre"],
    )

    assert result.exit_code != 0
    assert "Missing option '--track'" in result.output


# =============================================================================
#  extract-subs
# =============================================================================


def test_extract_subs_success_extracts_track(
    runner: CliRunner,
    video_mkv_subs: Path,
    tmp_path: Path,
) -> None:
    """`extract-subs` vuelca la pista indicada a un fichero srt."""
    output = tmp_path / "subs.srt"

    result = runner.invoke(
        app,
        [
            "extract-subs",
            str(video_mkv_subs),
            "--tracks",
            "0",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    extracted = list(tmp_path.glob("subs_subtitles_track_*.srt"))
    assert len(extracted) == 1
    assert "Hola prueba" in extracted[0].read_text(encoding="utf-8")


def test_extract_subs_error_incompatible_container(
    runner: CliRunner,
    video_mkv_subs: Path,
    tmp_path: Path,
) -> None:
    """`extract-subs` rechaza contenedores no compatibles con el códec srt."""
    result = runner.invoke(
        app,
        [
            "extract-subs",
            str(video_mkv_subs),
            "--tracks",
            "0",
            "-o",
            str(tmp_path / "subs.ass"),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code != 0
    assert "srt" in result.output


# =============================================================================
#  animated
# =============================================================================


def test_animated_success_generates_gif(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`animated --end` genera un gif limitado al rango temporal indicado."""
    output = tmp_path / "anim.gif"

    result = runner.invoke(
        app,
        [
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
        ],
    )

    assert result.exit_code == 0
    assert output.exists()
    assert stream_codec_names(output, "video") == ["gif"]


def test_animated_error_invalid_container(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`animated` rechaza salidas que no sean imágenes animadas."""
    result = runner.invoke(
        app,
        ["animated", str(video_mp4_a), "-o", str(tmp_path / "anim.mp4"), "-ov", "yes"],
    )

    assert result.exit_code != 0
    assert "Invalid extension .mp4" in result.output


# =============================================================================
#  frames
# =============================================================================


def test_frames_success_captures_at_timestamp(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`frames --at` captura una miniatura en cada marca indicada."""
    output = tmp_path / "thumb.jpg"

    result = runner.invoke(
        app,
        [
            "frames",
            str(video_mp4_a),
            "--at",
            "00:00:01",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    assert len(list(tmp_path.glob("thumb_*.jpg"))) == 1


def test_frames_error_invalid_timestamp(
    runner: CliRunner,
    video_mp4_a: Path,
) -> None:
    """`frames` rechaza marcas de tiempo con formato distinto de hh:mm:ss."""
    result = runner.invoke(app, ["frames", str(video_mp4_a), "--at", "zz:zz"])

    assert result.exit_code != 0
    assert "Invalid timestamp format" in result.output


# =============================================================================
#  interval
# =============================================================================


def test_interval_success_generates_series(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`interval --every` genera miniaturas periódicas numeradas."""
    output = tmp_path / "periodic.jpg"

    result = runner.invoke(
        app,
        ["interval", str(video_mp4_a), "--every", "1", "-o", str(output), "-ov", "yes"],
    )

    assert result.exit_code == 0
    assert len(list(tmp_path.glob("periodic_*.jpg"))) >= 1


def test_interval_error_missing_every(
    runner: CliRunner,
    video_mp4_a: Path,
) -> None:
    """`interval` exige la opción `--every` para calcular el periodo."""
    result = runner.invoke(app, ["interval", str(video_mp4_a)])

    assert result.exit_code != 0
    assert "Missing parameter: fps" in result.output


# =============================================================================
#  scene
# =============================================================================


def test_scene_success_detects_scene_changes(
    runner: CliRunner,
    video_scenes: Path,
    tmp_path: Path,
) -> None:
    """`scene --scene` captura una miniatura en cada corte detectado."""
    output = tmp_path / "scene.jpg"

    result = runner.invoke(
        app,
        [
            "scene",
            str(video_scenes),
            "--scene",
            "0.3",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    assert len(list(tmp_path.glob("scene_*.jpg"))) == 2


def test_scene_error_threshold_out_of_range(
    runner: CliRunner,
    video_scenes: Path,
) -> None:
    """`scene` valida que el umbral esté en el rango permitido por Typer."""
    result = runner.invoke(app, ["scene", str(video_scenes), "--scene", "5"])

    assert result.exit_code != 0
    assert "Invalid value for '--scene'" in result.output
