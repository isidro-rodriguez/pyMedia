"""Tests end-to-end de la superficie de la CLI de pyMedia.

Cada test usa la fixture `pymedia`, que ejecuta el mismo escenario como CLI en
proceso (`[cli]`) y como binario compilado (`[binary]`, marca `binary`). Se
comprueban el código de salida, los mensajes visibles y las propiedades de los
ficheros generados (vía ffprobe). Aquí viven los escenarios propios de cada
comando; las opciones compartidas entre comandos están parametrizadas en
`tests/test_cli_options.py`.
"""

import shutil
from pathlib import Path

import pytest
from helpers import (
    Invoke,
    ffprobe_duration,
    ffprobe_streams,
    stream_codec_names,
    stream_tag,
    stream_types,
    video_size,
)

# =============================================================================
#  info
# =============================================================================


def test_info_success_shows_metadata(pymedia: Invoke, video_mp4_a: Path) -> None:
    """`info` termina sin error y muestra la tabla de metadatos del vídeo."""
    result = pymedia("info", str(video_mp4_a))

    assert result.exit_code == 0
    assert "Metadata" in result.output


def test_info_with_subtitles(
    pymedia: Invoke,
    video_mkv_subs: Path,
) -> None:
    """`info` muestra la tabla de subtítulos con idioma y flags."""
    result = pymedia("info", str(video_mkv_subs))

    assert result.exit_code == 0
    assert "Metadata" in result.output
    assert "Subtitles" in result.output
    assert stream_tag(video_mkv_subs, "subtitle", "language", 0) is not None


def test_info_error_nonexistent_input(pymedia: Invoke, tmp_path: Path) -> None:
    """`info` con una ruta inexistente falla en la validación de Typer."""
    result = pymedia("info", str(tmp_path / "missing.mp4"))

    assert result.exit_code != 0
    assert "is not a file" in result.output


def test_info_success_with_debug(pymedia: Invoke, video_mp4_a: Path) -> None:
    """`info --debug` termina sin error mostrando los metadatos."""
    result = pymedia("info", str(video_mp4_a), "--debug")

    assert result.exit_code == 0
    assert "Metadata" in result.output


# =============================================================================
#  sheet
# =============================================================================


def test_sheet_success_generates_jpg(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`sheet --preset web` genera una imagen jpg con la rejilla de capturas."""
    output = tmp_path / "sheet.jpg"

    result = pymedia("sheet", str(video_mp4_a), "-o", str(output), "--preset", "web")

    assert result.exit_code == 0
    assert output.exists()
    assert stream_codec_names(output, "video") == ["mjpeg"]


def test_sheet_success_with_conflicting_name(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`sheet` dibuja el nombre aunque tenga `%`, comillas, comas o corchetes."""
    source = tmp_path / "100% real's, [2].mp4"
    shutil.copy(video_mp4_a, source)
    output = tmp_path / "sheet.jpg"

    result = pymedia("sheet", str(source), "-o", str(output), "--preset", "web")

    assert result.exit_code == 0
    assert output.exists()


def test_sheet_error_exclusive_output_options(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`sheet` rechaza `--output` y `--directory` usados a la vez."""
    result = pymedia(
        "sheet",
        str(video_mp4_a),
        "-o",
        str(tmp_path / "sheet.jpg"),
        "-d",
        str(tmp_path),
    )

    assert result.exit_code != 0
    assert "mutually exclusive" in result.output


def test_sheet_success_with_fhd_preset(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`sheet --preset fhd` genera una imagen jpg en resolución FHD."""
    output = tmp_path / "sheet_fhd.jpg"

    result = pymedia("sheet", str(video_mp4_a), "-o", str(output), "--preset", "fhd")

    assert result.exit_code == 0
    assert output.exists()


@pytest.mark.parametrize(
    ("preset", "width"), [("hd", 1280), ("fhd", 1920), ("web", 800)]
)
def test_sheet_preset_sets_width(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
    preset: str,
    width: int,
) -> None:
    """Cada `sheet --preset` genera la hoja con su ancho característico."""
    output = tmp_path / f"sheet_{preset}.jpg"

    result = pymedia("sheet", str(video_mp4_a), "-o", str(output), "--preset", preset)

    assert result.exit_code == 0
    assert video_size(output)[0] == width


def test_sheet_default_preset_is_hd(
    pymedia: Invoke, video_mp4_a: Path, tmp_path: Path
) -> None:
    """`sheet` sin `--preset` usa el preset `hd`."""
    output = tmp_path / "sheet_default.jpg"

    result = pymedia("sheet", str(video_mp4_a), "-o", str(output))

    assert result.exit_code == 0
    assert video_size(output)[0] == 1280


def test_sheet_success_with_overwrite_yes(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`sheet -ov yes` sobrescribe una imagen ya existente."""
    output = tmp_path / "sheet_overwrite.jpg"
    output.write_bytes(b"existing")

    result = pymedia("sheet", str(video_mp4_a), "-o", str(output), "-ov", "yes")

    assert result.exit_code == 0
    assert output.exists()
    assert output.read_bytes() != b"existing"


def test_sheet_success_with_directory(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`sheet --directory` genera la hoja dentro del directorio indicado."""
    directory = tmp_path / "sheets"

    result = pymedia(
        "sheet", str(video_mp4_a), "--directory", str(directory), "--preset", "web"
    )

    assert result.exit_code == 0
    generated = list(directory.glob("*_sheet.jpg"))
    assert len(generated) == 1


def test_sheet_success_multiple_inputs(
    pymedia: Invoke,
    video_mp4_a: Path,
    video_mp4_b: Path,
    tmp_path: Path,
) -> None:
    """`sheet` con múltiples entradas y `--directory` genera una hoja por vídeo."""
    directory = tmp_path / "sheets"

    result = pymedia(
        "sheet",
        str(video_mp4_a),
        str(video_mp4_b),
        "--directory",
        str(directory),
        "--preset",
        "web",
    )

    assert result.exit_code == 0
    generated = list(directory.glob("*_sheet.jpg"))
    assert len(generated) == 2


def test_sheet_header_truncates_long_track_list(
    pymedia: Invoke,
    video_mp4_multi_audio: Path,
    tmp_path: Path,
) -> None:
    """`sheet --preset web` recorta la cabecera con muchas pistas de audio."""
    output = tmp_path / "sheet.jpg"

    result = pymedia(
        "sheet", str(video_mp4_multi_audio), "-o", str(output), "--preset", "web"
    )

    assert result.exit_code == 0
    assert output.exists()


# =============================================================================
#  join
# =============================================================================


def test_join_success_concatenates_videos(
    pymedia: Invoke,
    video_mp4_a: Path,
    video_mp4_b: Path,
    tmp_path: Path,
) -> None:
    """`join` une dos vídeos en un contenedor con la duración combinada."""
    output = tmp_path / "joined.mp4"

    result = pymedia(
        "join", str(video_mp4_a), str(video_mp4_b), "-o", str(output), "-ov", "yes"
    )

    assert result.exit_code == 0
    assert ffprobe_duration(output) >= 3.5


def test_join_error_single_input(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`join` con un único vídeo exige al menos dos entradas."""
    result = pymedia("join", str(video_mp4_a), "-o", str(tmp_path / "joined.mp4"))

    assert result.exit_code != 0
    assert "at least 2 videos" in result.output


def test_join_success_with_overwrite_yes(
    pymedia: Invoke,
    video_mp4_a: Path,
    video_mp4_b: Path,
    tmp_path: Path,
) -> None:
    """`join -ov yes` sobrescribe el fichero de salida existente."""
    output = tmp_path / "joined.mp4"
    output.write_bytes(b"existing")

    result = pymedia(
        "join", str(video_mp4_a), str(video_mp4_b), "-o", str(output), "-ov", "yes"
    )

    assert result.exit_code == 0
    assert output.exists()
    assert output.read_bytes() != b"existing"


# -- Join con vídeos incompatibles -------------------------------------------

JOIN_INCOMPATIBLE_CASES = [
    pytest.param(
        "video_mp4_diff_codec",
        "video.codec differs:",
        id="codec",
    ),
    pytest.param(
        "video_mp4_diff_res",
        "video.width differs:",
        id="resolution",
    ),
    pytest.param(
        "video_mp4_diff_fps",
        "video.fps differs:",
        id="fps",
    ),
    pytest.param(
        "video_mp4_diff_pixfmt",
        "video.pix_fmt differs:",
        id="pix_fmt",
    ),
    pytest.param(
        "video_mp4_diff_sr",
        "audio[0].sample_rate differs:",
        id="sample_rate",
    ),
    pytest.param(
        "video_mp4_diff_audio_codec",
        "audio[0].codec differs:",
        id="audio_codec",
    ),
]


@pytest.mark.parametrize("second_fixture,expected", JOIN_INCOMPATIBLE_CASES)
def test_join_rejects_incompatible_media(
    pymedia: Invoke,
    request: pytest.FixtureRequest,
    video_mp4_a: Path,
    second_fixture: str,
    expected: str,
    tmp_path: Path,
) -> None:
    """`join` rechaza vídeos incompatibles indicando el motivo."""
    second = request.getfixturevalue(second_fixture)
    output = tmp_path / "joined.mp4"

    result = pymedia(
        "join",
        str(video_mp4_a),
        str(second),
        "-o",
        str(output),
        "-ov",
        "yes",
    )

    assert result.exit_code != 0
    assert "Incompatible media files" in result.output
    assert expected in result.output
    assert output.exists() is False


def test_join_rejects_no_audio_first(
    pymedia: Invoke,
    video_no_audio: Path,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`join` rechaza si el primero no tiene audio y el segundo sí."""
    output = tmp_path / "joined.mp4"

    result = pymedia(
        "join",
        str(video_no_audio),
        str(video_mp4_a),
        "-o",
        str(output),
        "-ov",
        "yes",
    )

    assert result.exit_code != 0
    assert "Incompatible media files" in result.output
    assert "audio presence differs: first has no audio, this has audio" in result.output
    assert output.exists() is False


# -- Join con vídeos compatibles --------------------------------------------


def test_join_success_multiple_compatible(
    pymedia: Invoke,
    video_mp4_a: Path,
    video_mp4_b: Path,
    tmp_path: Path,
) -> None:
    """`join` une tres vídeos compatibles."""
    output = tmp_path / "joined.mp4"

    result = pymedia(
        "join",
        str(video_mp4_a),
        str(video_mp4_b),
        str(video_mp4_a),
        "-o",
        str(output),
        "-ov",
        "yes",
    )

    assert result.exit_code == 0
    assert ffprobe_duration(output) >= 5.5


# =============================================================================
#  remux
# =============================================================================


def test_remux_success_changes_container(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`remux` copia los streams a un contenedor distinto sin recodificar."""
    output = tmp_path / "remuxed.mkv"

    result = pymedia("remux", str(video_mp4_a), "-o", str(output), "-ov", "yes")

    assert result.exit_code == 0
    assert output.exists()
    assert stream_types(output) == ["video", "audio"]


def test_remux_error_fast_start_non_mp4(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`remux` rechaza `--fast-start` con un contenedor distinto de mp4."""
    result = pymedia(
        "remux", str(video_mp4_a), "-o", str(tmp_path / "remuxed.mkv"), "--fast-start"
    )

    assert result.exit_code != 0
    assert "Fast start only works" in result.output


def test_remux_success_with_genpts(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`remux --genpts` regenera los marcadores de tiempo."""
    output = tmp_path / "remuxed_genpts.mkv"

    result = pymedia(
        "remux", str(video_mp4_a), "-o", str(output), "--genpts", "-ov", "yes"
    )

    assert result.exit_code == 0
    assert output.exists()
    assert stream_types(output) == ["video", "audio"]


def test_remux_success_with_sort_tracks(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`remux --sort-tracks` ordena las pistas del contenedor."""
    output = tmp_path / "remuxed_sorted.mkv"

    result = pymedia(
        "remux", str(video_mp4_a), "-o", str(output), "--sort-tracks", "-ov", "yes"
    )

    assert result.exit_code == 0
    assert output.exists()
    assert stream_types(output) == ["video", "audio"]


def test_remux_error_change_incompatible_container(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`remux` rechaza cambiar a un contenedor incompatible con el códec."""
    output = tmp_path / "remuxed.webm"

    result = pymedia("remux", str(video_mp4_a), "-o", str(output), "-ov", "yes")

    assert result.exit_code != 0


# =============================================================================
#  cut
# =============================================================================


def test_cut_success_cuts_at_timestamp(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`cut --at` divide el vídeo en un segmento por cada marca."""
    output = tmp_path / "part.mp4"

    result = pymedia(
        "cut", str(video_mp4_a), "--at", "00:00:01", "-o", str(output), "-ov", "yes"
    )

    assert result.exit_code == 0
    parts = sorted(tmp_path.glob("part_*.mp4"))
    assert len(parts) == 2
    assert all(ffprobe_duration(part) < 1.9 for part in parts)


def test_cut_error_missing_options(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`cut` exige una de `--at`, `--start` o `--end`."""
    result = pymedia("cut", str(video_mp4_a), "-o", str(tmp_path / "part.mp4"))

    assert result.exit_code != 0
    normalized = " ".join(result.output.split())
    assert "Missing at least one of these options: at, start, end" in normalized


def test_cut_success_with_start(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`cut --start` divide el vídeo desde una marca hasta el final."""
    output = tmp_path / "from_start.mp4"

    result = pymedia(
        "cut", str(video_mp4_a), "--start", "00:00:01", "-o", str(output), "-ov", "yes"
    )

    assert result.exit_code == 0
    assert output.exists()
    assert ffprobe_duration(output) < 1.9


def test_cut_success_with_end(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`cut --end` divide el vídeo desde el inicio hasta una marca."""
    output = tmp_path / "from_end.mp4"

    result = pymedia(
        "cut", str(video_mp4_a), "--end", "00:00:01", "-o", str(output), "-ov", "yes"
    )

    assert result.exit_code == 0
    assert output.exists()
    assert ffprobe_duration(output) < 1.9


def test_cut_error_ambiguous_at_start(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`cut` rechaza combinar `--at` con `--start`."""
    result = pymedia(
        "cut",
        str(video_mp4_a),
        "--at",
        "00:00:01",
        "--start",
        "00:00:00",
        "-o",
        str(tmp_path / "part.mp4"),
    )

    assert result.exit_code != 0
    assert "Ambiguous options" in result.output


def test_cut_error_ambiguous_at_end(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`cut` rechaza combinar `--at` con `--end`."""
    result = pymedia(
        "cut",
        str(video_mp4_a),
        "--at",
        "00:00:01",
        "--end",
        "00:00:02",
        "-o",
        str(tmp_path / "part.mp4"),
    )

    assert result.exit_code != 0
    assert "Ambiguous options" in result.output


def test_cut_error_start_bigger_end(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`cut` rechaza `--start` posterior a `--end`."""
    result = pymedia(
        "cut",
        str(video_mp4_a),
        "--start",
        "00:00:02",
        "--end",
        "00:00:01",
        "-o",
        str(tmp_path / "part.mp4"),
    )

    assert result.exit_code != 0


def test_cut_error_duplicate_timestamps(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`cut` rechaza marcas de tiempo duplicadas en `--at`."""
    result = pymedia(
        "cut",
        str(video_mp4_a),
        "--at",
        "00:00:01,00:00:01",
        "-o",
        str(tmp_path / "part.mp4"),
    )

    assert result.exit_code != 0
    assert "duplicated timestamp" in result.output


# =============================================================================
#  transcode
# =============================================================================


def test_transcode_success_transcodes_video(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`transcode --video` recodifica la pista con el preset por defecto."""
    output = tmp_path / "transcoded.mp4"

    result = pymedia(
        "transcode", str(video_mp4_a), "--video", "-o", str(output), "-ov", "yes"
    )

    assert result.exit_code == 0
    assert stream_codec_names(output, "video") == ["hevc"]


def test_transcode_success_burns_subtitles(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`transcode --burn-subtitles` quema el fichero srt indicado en el vídeo."""
    subtitle = tmp_path / "eng_subs.srt"
    subtitle.write_text(
        "1\n00:00:00,000 --> 00:00:02,000\nHello test\n", encoding="utf-8"
    )
    output = tmp_path / "burned.mp4"

    result = pymedia(
        "transcode",
        str(video_mp4_a),
        "--burn-subtitles",
        str(subtitle),
        "-o",
        str(output),
        "-ov",
        "yes",
    )

    assert result.exit_code == 0
    assert output.exists()


@pytest.mark.parametrize("name", ["Joan's first bycicle, [2].srt", "mi fichero.srt"])
def test_transcode_burns_subtitles_with_conflicting_name(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
    name: str,
) -> None:
    """`transcode --burn-subtitles` admite nombres con comillas, comas y espacios."""
    subtitle = tmp_path / name
    subtitle.write_text(
        "1\n00:00:00,000 --> 00:00:02,000\nHello test\n", encoding="utf-8"
    )
    output = tmp_path / "burned.mp4"

    result = pymedia(
        "transcode",
        str(video_mp4_a),
        "--burn-subtitles",
        str(subtitle),
        "--size",
        "64x36",
        "-o",
        str(output),
        "-ov",
        "yes",
    )

    assert result.exit_code == 0
    assert output.exists()


def test_transcode_error_missing_action(
    pymedia: Invoke,
    video_mp4_a: Path,
) -> None:
    """`transcode` sin ninguna opción de transcodificación avisa de las requeridas."""
    result = pymedia("transcode", str(video_mp4_a))

    assert result.exit_code != 0
    output = result.output.replace("\u2502", " ").replace("\u250c", " ")
    normalized = " ".join(output.split())
    assert "Missing at least one of these options:" in normalized
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


def test_transcode_error_invalid_audio_input(
    pymedia: Invoke,
    audio_m4a: Path,
) -> None:
    """`transcode` rechaza ficheros de audio como entrada.

    Son contenedores inválidos para un comando que exige vídeo.
    """
    result = pymedia(
        "transcode", str(audio_m4a), "--video", "-o", str(audio_m4a.parent / "out.mp4")
    )

    assert result.exit_code != 0
    normalized = " ".join(result.output.split())
    assert "Invalid extension .m4a" in normalized
    assert "Video requires one of:" in normalized


@pytest.mark.parametrize("preset", ["fast", "even", "slow"])
def test_transcode_success_with_preset(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
    preset: str,
) -> None:
    """`transcode --preset` recodifica el vídeo a hevc con cada perfil."""
    output = tmp_path / f"transcoded_{preset}.mp4"

    result = pymedia(
        "transcode",
        str(video_mp4_a),
        "--preset",
        preset,
        "--video",
        "-o",
        str(output),
        "-ov",
        "yes",
    )

    assert result.exit_code == 0
    assert stream_codec_names(output, "video") == ["hevc"]


def test_transcode_success_default_preset_is_even(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`transcode` sin `--preset` usa el perfil `even` (hevc)."""
    output = tmp_path / "transcoded_default.mp4"

    result = pymedia(
        "transcode", str(video_mp4_a), "--video", "-o", str(output), "-ov", "yes"
    )

    assert result.exit_code == 0
    assert stream_codec_names(output, "video") == ["hevc"]


@pytest.mark.parametrize("command", [("sheet",), ("transcode", "--video")])
def test_output_with_multiple_inputs_is_rejected(
    pymedia: Invoke,
    video_mp4_a: Path,
    video_mp4_b: Path,
    tmp_path: Path,
    command: tuple[str, ...],
) -> None:
    """`-o` con varias entradas se rechaza en favor de `--directory`."""
    result = pymedia(
        command[0],
        str(video_mp4_a),
        str(video_mp4_b),
        *command[1:],
        "-o",
        str(tmp_path / "out.mp4"),
    )

    assert result.exit_code != 0
    assert "not allowed to specify an output with multiple inputs" in result.output


@pytest.mark.parametrize(
    ("command", "pattern"),
    [(("sheet",), "*_sheet.jpg"), (("transcode", "--video"), "*_transcoded.mp4")],
)
def test_directory_with_multiple_inputs_generates_one_output_each(
    pymedia: Invoke,
    video_mp4_a: Path,
    video_mp4_b: Path,
    tmp_path: Path,
    command: tuple[str, ...],
    pattern: str,
) -> None:
    """`--directory` procesa cada entrada y deja una salida por fichero."""
    directory = tmp_path / "batch"

    result = pymedia(
        command[0],
        str(video_mp4_a),
        str(video_mp4_b),
        *command[1:],
        "-d",
        str(directory),
        "-ov",
        "yes",
    )

    assert result.exit_code == 0
    assert len(list(directory.glob(pattern))) == 2


def test_transcode_success_transcode_audio(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`transcode --audio` recodifica la pista de audio."""
    output = tmp_path / "transcoded_audio.mp4"

    result = pymedia(
        "transcode", str(video_mp4_a), "--audio", "0", "-o", str(output), "-ov", "yes"
    )

    assert result.exit_code == 0
    assert output.exists()


# =============================================================================
#  add-audio
# =============================================================================


def test_add_audio_success_inserts_track(
    pymedia: Invoke,
    video_mkv: Path,
    audio_m4a: Path,
    tmp_path: Path,
) -> None:
    """`add-audio` añade la pista externa con su idioma al contenedor."""
    output = tmp_path / "with_audio.mkv"

    result = pymedia(
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

    assert result.exit_code == 0
    audio_streams = [
        stream
        for stream in ffprobe_streams(output)
        if stream.get("codec_type") == "audio"
    ]
    assert len(audio_streams) == 2
    assert (audio_streams[1].get("tags") or {}).get("language") == "eng"


def test_add_audio_error_missing_language(
    pymedia: Invoke,
    video_mkv: Path,
    audio_m4a: Path,
    tmp_path: Path,
) -> None:
    """`add-audio` exige la opción `--language` para la nueva pista."""
    result = pymedia(
        "add-audio",
        str(video_mkv),
        str(audio_m4a),
        "-o",
        str(tmp_path / "with_audio.mkv"),
    )

    assert result.exit_code != 0
    assert "Missing option '--language'" in result.output


def test_add_audio_error_audio_file_missing(
    pymedia: Invoke, video_mkv: Path, tmp_path: Path
) -> None:
    """`add-audio` rechaza un fichero de audio que no existe."""
    result = pymedia(
        "add-audio",
        str(video_mkv),
        str(tmp_path / "missing.m4a"),
        "--language",
        "eng",
        "-o",
        str(tmp_path / "out.mkv"),
    )

    assert result.exit_code != 0
    assert "is not a file" in result.output


# =============================================================================
#  delete-audio
# =============================================================================


def test_delete_audio_success_removes_tracks(
    pymedia: Invoke,
    video_mkv: Path,
    tmp_path: Path,
) -> None:
    """`delete-audio` elimina las pistas indicadas del contenedor."""
    output = tmp_path / "no_audio.mkv"

    result = pymedia(
        "delete-audio", str(video_mkv), "--tracks", "0", "-o", str(output), "-ov", "yes"
    )

    assert result.exit_code == 0
    assert "audio" not in stream_types(output)


def test_delete_audio_error_without_audio_tracks(
    pymedia: Invoke,
    video_no_audio: Path,
    tmp_path: Path,
) -> None:
    """`delete-audio` avisa cuando el medio no tiene pistas de audio."""
    result = pymedia(
        "delete-audio",
        str(video_no_audio),
        "--tracks",
        "0",
        "-o",
        str(tmp_path / "out.mp4"),
        "-ov",
        "yes",
    )

    assert result.exit_code != 0
    assert "Missing parameter: media.audio" in result.output


# =============================================================================
#  edit-audio
# =============================================================================


def test_edit_audio_success_updates_metadata(
    pymedia: Invoke,
    video_mkv: Path,
    tmp_path: Path,
) -> None:
    """`edit-audio` actualiza el idioma y el título de la pista indicada."""
    output = tmp_path / "edited_audio.mkv"

    result = pymedia(
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

    assert result.exit_code == 0
    assert stream_tag(output, "audio", "language") == "fre"
    assert stream_tag(output, "audio", "title") == "Edited"


def test_edit_audio_error_missing_track(
    pymedia: Invoke,
    video_mkv: Path,
) -> None:
    """`edit-audio` exige la opción `--track` para identificar la pista."""
    result = pymedia("edit-audio", str(video_mkv), "--language", "fre")

    assert result.exit_code != 0
    assert "Missing option '--track'" in result.output


def test_edit_audio_error_missing_metadata(
    pymedia: Invoke,
    video_mkv: Path,
) -> None:
    """`edit-audio` exige al menos una opción de metadatos."""
    result = pymedia("edit-audio", str(video_mkv), "--track", "0")

    assert result.exit_code != 0
    normalized = " ".join(result.output.split())
    assert "Missing at least one of these options:" in normalized


def test_delete_audio_error_track_out_of_range(
    pymedia: Invoke, video_mkv: Path, tmp_path: Path
) -> None:
    """`delete-audio` rechaza un índice de pista inexistente."""
    result = pymedia(
        "delete-audio",
        str(video_mkv),
        "--tracks",
        "5",
        "-o",
        str(tmp_path / "out.mkv"),
        "-ov",
        "yes",
    )

    assert result.exit_code != 0
    assert "Audio index not included" in result.output


# =============================================================================
#  extract-audio
# =============================================================================


def test_extract_audio_success_extracts_track(
    pymedia: Invoke,
    video_mkv: Path,
    tmp_path: Path,
) -> None:
    """`extract-audio` vuelca la pista indicada a un fichero de audio."""
    output = tmp_path / "audio.m4a"

    result = pymedia(
        "extract-audio",
        str(video_mkv),
        "--tracks",
        "0",
        "-o",
        str(output),
        "-ov",
        "yes",
    )

    assert result.exit_code == 0
    extracted = list(tmp_path.glob("audio_audio_track_*.m4a"))
    assert len(extracted) == 1
    assert "audio" in stream_types(extracted[0])


def test_extract_audio_error_without_audio_tracks(
    pymedia: Invoke,
    video_no_audio: Path,
) -> None:
    """`extract-audio` avisa cuando el medio no tiene pistas de audio."""
    result = pymedia("extract-audio", str(video_no_audio), "--tracks", "0")

    assert result.exit_code != 0
    assert "Missing parameter: media.audio" in result.output


# =============================================================================
#  add-subs
# =============================================================================


def test_add_subs_success_inserts_track(
    pymedia: Invoke,
    video_mkv: Path,
    subs_spa: Path,
    tmp_path: Path,
) -> None:
    """`add-subs` inserta el fichero externo como pista con su idioma."""
    output = tmp_path / "with_subs.mkv"

    result = pymedia(
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

    assert result.exit_code == 0
    sub_streams = [
        stream
        for stream in ffprobe_streams(output)
        if stream.get("codec_type") == "subtitle"
    ]
    assert len(sub_streams) == 1
    assert (sub_streams[0].get("tags") or {}).get("language") == "spa"


def test_add_subs_error_invalid_subtitles_file(
    pymedia: Invoke,
    video_mkv: Path,
    subs_bad: Path,
    tmp_path: Path,
) -> None:
    """`add-subs` rechaza ficheros con extensión srt pero contenido inválido."""
    result = pymedia(
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

    assert result.exit_code != 0
    # El mensaje de ffprobe puede partirse en varias líneas con espacios extra
    output = " ".join(result.output.split())
    assert "Invalid data found" in output
    assert "when processing input" in output


def test_add_subs_mp4_mov_text(
    pymedia: Invoke,
    video_mp4_a: Path,
    subs_spa: Path,
    tmp_path: Path,
) -> None:
    """`add-subs` con salida .mp4 usa el códec `mov_text`."""
    output = tmp_path / "subs.mp4"

    result = pymedia(
        "add-subs",
        str(video_mp4_a),
        str(subs_spa),
        "--language",
        "spa",
        "-o",
        str(output),
        "-ov",
        "yes",
    )

    assert result.exit_code == 0
    codecs = stream_codec_names(output, "subtitle")
    assert "mov_text" in codecs


def test_add_subs_webm_webvtt(
    pymedia: Invoke,
    video_webm_vp8: Path,
    subs_spa: Path,
    tmp_path: Path,
) -> None:
    """`add-subs` con salida .webm usa el códec `webvtt`."""
    output = tmp_path / "subs.webm"

    result = pymedia(
        "add-subs",
        str(video_webm_vp8),
        str(subs_spa),
        "--language",
        "spa",
        "-o",
        str(output),
        "-ov",
        "yes",
    )

    assert result.exit_code == 0
    codecs = stream_codec_names(output, "subtitle")
    assert "webvtt" in codecs


# Extensiones de salida que `MediaOutputMixin` rechaza por no estar en
# SUPPORTED.CONTAINERS (.mkv, .mp4, .webm), incluso las que `_process_codec`
# sí sabría mapear (.mov, .ts).
UNSUPPORTED_SUBS_OUTPUTS = [
    pytest.param(".avi", id="avi"),
    pytest.param(".mov", id="mov"),
    pytest.param(".ts", id="ts"),
]


@pytest.mark.parametrize("suffix", UNSUPPORTED_SUBS_OUTPUTS)
def test_add_subs_unsupported_container(
    pymedia: Invoke,
    video_mp4_a: Path,
    subs_spa: Path,
    suffix: str,
    tmp_path: Path,
) -> None:
    """`add-subs` solo admite .mkv, .mp4 y .webm como contenedor de salida.

    El mensaje «Subtitles codec not supported.» de `_process_codec` es
    inalcanzable desde la CLI: `MediaOutputMixin` corta antes cualquier extensión
    fuera de `SUPPORTED.CONTAINERS` y las tres admitidas tienen códec asignado.
    """
    output = tmp_path / f"out{suffix}"

    result = pymedia(
        "add-subs",
        str(video_mp4_a),
        str(subs_spa),
        "--language",
        "spa",
        "-o",
        str(output),
        "-ov",
        "yes",
    )

    assert result.exit_code != 0
    assert f"Invalid extension {suffix}" in result.output
    assert not output.exists()


# Formatos de subtítulo aceptados como entrada; el srt ya se cubre en
# `test_add_subs_success_inserts_track`.
SUBS_INPUT_FORMATS = [
    pytest.param("subs_ass", id="ass"),
    pytest.param("subs_vtt", id="vtt"),
]


@pytest.mark.parametrize("fixture_name", SUBS_INPUT_FORMATS)
def test_add_subs_input_formats(
    pymedia: Invoke,
    request: pytest.FixtureRequest,
    video_mkv: Path,
    fixture_name: str,
    tmp_path: Path,
) -> None:
    """`add-subs` acepta entradas .ass y .vtt y usa el códec del contenedor."""
    output = tmp_path / "with_subs.mkv"

    result = pymedia(
        "add-subs",
        str(video_mkv),
        str(request.getfixturevalue(fixture_name)),
        "--language",
        "spa",
        "-o",
        str(output),
        "-ov",
        "yes",
    )

    assert result.exit_code == 0
    assert stream_codec_names(output, "subtitle") == ["subrip"]
    assert stream_tag(output, "subtitle", "language") == "spa"


def test_add_subs_missing_subtitles_file(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`add-subs` rechaza fichero de subtítulos inexistente."""
    result = pymedia(
        "add-subs",
        str(video_mp4_a),
        str(tmp_path / "missing.srt"),
        "--language",
        "spa",
        "-o",
        str(tmp_path / "with_subs.mp4"),
        "-ov",
        "yes",
    )

    assert result.exit_code != 0
    assert "is not a file" in result.output


def test_add_subs_invalid_extension(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`add-subs` rechaza fichero de subtítulos con extensión inválida."""
    bad_subs = tmp_path / "bad.txt"
    bad_subs.write_text("1\n00:00:00,000 --> 00:00:01,000\nHola\n", encoding="utf-8")

    result = pymedia(
        "add-subs",
        str(video_mp4_a),
        str(bad_subs),
        "--language",
        "spa",
        "-o",
        str(tmp_path / "with_subs.mp4"),
        "-ov",
        "yes",
    )

    assert result.exit_code != 0
    assert "Invalid extension" in result.output


def test_add_audio_invalid_extension(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`add-audio` rechaza fichero de audio con extensión inválida."""
    bad_audio = tmp_path / "bad.txt"
    bad_audio.write_text("dummy", encoding="utf-8")

    result = pymedia(
        "add-audio",
        str(video_mp4_a),
        str(bad_audio),
        "--language",
        "eng",
        "-o",
        str(tmp_path / "with_audio.mp4"),
        "-ov",
        "yes",
    )

    assert result.exit_code != 0
    assert "Invalid extension" in result.output


# =============================================================================
#  delete-subs
# =============================================================================


def test_delete_subs_success_removes_track(
    pymedia: Invoke,
    video_mkv_subs: Path,
    tmp_path: Path,
) -> None:
    """`delete-subs` elimina las pistas indicadas y conserva el resto."""
    output = tmp_path / "fewer_subs.mkv"

    result = pymedia(
        "delete-subs",
        str(video_mkv_subs),
        "--tracks",
        "1",
        "-o",
        str(output),
        "-ov",
        "yes",
    )

    assert result.exit_code == 0
    languages = [
        (stream.get("tags") or {}).get("language")
        for stream in ffprobe_streams(output)
        if stream.get("codec_type") == "subtitle"
    ]
    assert languages == ["spa"]


def test_delete_subs_error_without_subtitles(
    pymedia: Invoke,
    video_mkv: Path,
    tmp_path: Path,
) -> None:
    """`delete-subs` avisa cuando el medio no tiene pistas de subtítulos."""
    result = pymedia(
        "delete-subs",
        str(video_mkv),
        "--tracks",
        "0",
        "-o",
        str(tmp_path / "out.mkv"),
        "-ov",
        "yes",
    )

    assert result.exit_code != 0
    assert "Missing parameter: media.subtitles" in result.output


def test_delete_subs_success_multiple_tracks(
    pymedia: Invoke,
    video_mkv_subs: Path,
    tmp_path: Path,
) -> None:
    """`delete-subs --tracks 0,1` elimina ambas pistas de subtítulos."""
    output = tmp_path / "no_subs.mkv"

    result = pymedia(
        "delete-subs",
        str(video_mkv_subs),
        "--tracks",
        "0,1",
        "-o",
        str(output),
        "-ov",
        "yes",
    )

    assert result.exit_code == 0
    assert "subtitle" not in stream_types(output)


# =============================================================================
#  edit-subs
# =============================================================================


def test_edit_subs_success_updates_metadata(
    pymedia: Invoke,
    video_mkv_subs: Path,
    tmp_path: Path,
) -> None:
    """`edit-subs` actualiza el idioma de la pista de subtítulos indicada."""
    output = tmp_path / "edited_subs.mkv"

    result = pymedia(
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

    assert result.exit_code == 0
    assert stream_tag(output, "subtitle", "language") == "fre"


def test_edit_subs_error_missing_track(
    pymedia: Invoke,
    video_mkv_subs: Path,
) -> None:
    """`edit-subs` exige la opción `--track` para identificar la pista."""
    result = pymedia("edit-subs", str(video_mkv_subs), "--language", "fre")

    assert result.exit_code != 0
    assert "Missing option '--track'" in result.output


def test_edit_subs_error_missing_metadata(
    pymedia: Invoke,
    video_mkv_subs: Path,
) -> None:
    """`edit-subs` exige al menos una opción de metadatos."""
    result = pymedia("edit-subs", str(video_mkv_subs), "--track", "0")

    assert result.exit_code != 0
    normalized = " ".join(result.output.split())
    assert "Missing at least one of these options:" in normalized


# =============================================================================
#  extract-subs
# =============================================================================


def test_extract_subs_success_extracts_track(
    pymedia: Invoke,
    video_mkv_subs: Path,
    tmp_path: Path,
) -> None:
    """`extract-subs` vuelca la pista indicada a un fichero srt."""
    output = tmp_path / "subs.srt"

    result = pymedia(
        "extract-subs",
        str(video_mkv_subs),
        "--tracks",
        "0",
        "-o",
        str(output),
        "-ov",
        "yes",
    )

    assert result.exit_code == 0
    extracted = list(tmp_path.glob("subs_subtitles_track_*.srt"))
    assert len(extracted) == 1
    assert "Hola prueba" in extracted[0].read_text(encoding="utf-8")


def test_extract_subs_error_incompatible_container(
    pymedia: Invoke,
    video_mkv_subs: Path,
    tmp_path: Path,
) -> None:
    """`extract-subs` rechaza contenedores no compatibles con el códec srt."""
    result = pymedia(
        "extract-subs",
        str(video_mkv_subs),
        "--tracks",
        "0",
        "-o",
        str(tmp_path / "subs.ass"),
        "-ov",
        "yes",
    )

    assert result.exit_code != 0
    assert "srt" in result.output


def test_extract_subs_success_multiple_tracks(
    pymedia: Invoke,
    video_mkv_subs: Path,
    tmp_path: Path,
) -> None:
    """`extract-subs --tracks 0,1` extrae ambas pistas de subtítulos."""
    output = tmp_path / "subs.srt"

    result = pymedia(
        "extract-subs",
        str(video_mkv_subs),
        "--tracks",
        "0,1",
        "-o",
        str(output),
        "-ov",
        "yes",
    )

    assert result.exit_code == 0
    extracted = list(tmp_path.glob("subs_subtitles_track_*.srt"))
    assert len(extracted) == 2


# =============================================================================
#  animated
# =============================================================================


def test_animated_success_generates_gif(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`animated --end` genera un gif limitado al rango temporal indicado."""
    output = tmp_path / "anim.gif"

    result = pymedia(
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

    assert result.exit_code == 0
    assert output.exists()
    assert stream_codec_names(output, "video") == ["gif"]


def test_animated_error_invalid_container(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`animated` rechaza salidas que no sean imágenes animadas."""
    result = pymedia(
        "animated", str(video_mp4_a), "-o", str(tmp_path / "anim.mp4"), "-ov", "yes"
    )

    assert result.exit_code != 0
    assert "Invalid extension .mp4" in result.output


def test_animated_success_with_range(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`animated --start --end` genera gif limitado al rango."""
    output = tmp_path / "anim_range.gif"

    result = pymedia(
        "animated",
        str(video_mp4_a),
        "-o",
        str(output),
        "-ov",
        "yes",
        "--start",
        "00:00:00",
        "--end",
        "00:00:01",
    )

    assert result.exit_code == 0
    assert output.exists()


def test_animated_success_with_fps_15(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`animated --fps 15` genera gif a 15 fps."""
    output = tmp_path / "anim_fps15.gif"

    result = pymedia(
        "animated", str(video_mp4_a), "-o", str(output), "-ov", "yes", "--fps", "15"
    )

    assert result.exit_code == 0
    assert output.exists()


def test_animated_error_fps_out_of_range(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`animated --fps 3` rechaza fps fuera del rango."""
    result = pymedia(
        "animated", str(video_mp4_a), "-o", str(tmp_path / "anim.gif"), "--fps", "3"
    )

    assert result.exit_code != 0
    assert "Invalid value for '--fps'" in result.output


def test_animated_success_generates_apng(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`animated -o output.apng` genera una imagen APNG."""
    output = tmp_path / "anim.apng"

    result = pymedia(
        "animated", str(video_mp4_a), "-o", str(output), "-ov", "yes", "--fps", "10"
    )

    assert result.exit_code == 0
    assert output.exists()
    assert stream_codec_names(output, "video") == ["apng"]


def test_animated_success_generates_webp(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`animated -o output.webp` genera una imagen WebP animada."""
    output = tmp_path / "anim.webp"

    result = pymedia(
        "animated", str(video_mp4_a), "-o", str(output), "-ov", "yes", "--fps", "10"
    )

    assert result.exit_code == 0
    assert output.exists()


# =============================================================================
#  frames
# =============================================================================


def test_frames_success_captures_at_timestamp(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`frames --at` captura una miniatura en cada marca indicada."""
    output = tmp_path / "thumb.jpg"

    result = pymedia(
        "frames", str(video_mp4_a), "--at", "00:00:01", "-o", str(output), "-ov", "yes"
    )

    assert result.exit_code == 0
    assert len(list(tmp_path.glob("thumb_*.jpg"))) == 1


def test_frames_error_invalid_timestamp(
    pymedia: Invoke,
    video_mp4_a: Path,
) -> None:
    """`frames` rechaza marcas de tiempo con formato distinto de hh:mm:ss."""
    result = pymedia("frames", str(video_mp4_a), "--at", "zz:zz")

    assert result.exit_code != 0
    assert "Invalid timestamp format" in result.output


def test_frames_success_multiple_timestamps(
    pymedia: Invoke, video_mp4_a: Path, tmp_path: Path
) -> None:
    """`frames --at a,b` captura un fotograma por cada instante."""
    output = tmp_path / "multi.jpg"

    result = pymedia(
        "frames",
        str(video_mp4_a),
        "--at",
        "00:00:00,00:00:01",
        "-o",
        str(output),
        "-ov",
        "yes",
    )

    assert result.exit_code == 0
    assert len(list(tmp_path.glob("multi_*.jpg"))) == 2


IMAGE_FORMAT_CASES = [
    pytest.param(".png", "png", id="png"),
    pytest.param(".webp", "webp", id="webp"),
]


@pytest.mark.parametrize("ext,codec", IMAGE_FORMAT_CASES)
def test_frames_output_format(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
    ext: str,
    codec: str,
) -> None:
    """`frames` genera imágenes en distintos formatos."""
    output = tmp_path / f"thumb{ext}"

    result = pymedia(
        "frames",
        str(video_mp4_a),
        "--at",
        "00:00:01",
        "-o",
        str(output),
        "-ov",
        "yes",
    )

    assert result.exit_code == 0
    generated = list(output.parent.glob(f"thumb_*{ext}"))
    assert len(generated) == 1
    codecs = stream_codec_names(generated[0], "video")
    assert codecs[0] == codec


# =============================================================================
#  interval
# =============================================================================


def test_interval_success_generates_series(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`interval --every` genera miniaturas periódicas numeradas."""
    output = tmp_path / "periodic.jpg"

    result = pymedia(
        "interval", str(video_mp4_a), "--every", "1", "-o", str(output), "-ov", "yes"
    )

    assert result.exit_code == 0
    assert len(list(tmp_path.glob("periodic_*.jpg"))) >= 1


def test_interval_success_with_range(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`interval --start --end` genera miniaturas en el rango indicado."""
    output = tmp_path / "periodic_range.jpg"

    result = pymedia(
        "interval",
        str(video_mp4_a),
        "--every",
        "1",
        "-o",
        str(output),
        "-ov",
        "yes",
        "--start",
        "00:00:00",
        "--end",
        "00:00:01",
    )

    assert result.exit_code == 0
    assert len(list(tmp_path.glob("periodic_range_*.jpg"))) >= 1


def test_interval_error_every_too_small(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`interval --every 0` rechaza periodo menor a 1 segundo."""
    result = pymedia(
        "interval", str(video_mp4_a), "--every", "0", "-o", str(tmp_path / "p.jpg")
    )

    assert result.exit_code != 0
    assert "Interval must be at least 1 second" in result.output


# =============================================================================
#  scene
# =============================================================================


def test_scene_success_detects_scene_changes(
    pymedia: Invoke,
    video_scenes: Path,
    tmp_path: Path,
) -> None:
    """`scene --scene` captura una miniatura en cada corte detectado."""
    output = tmp_path / "scene.jpg"

    result = pymedia(
        "scene", str(video_scenes), "--scene", "0.3", "-o", str(output), "-ov", "yes"
    )

    assert result.exit_code == 0
    assert len(list(tmp_path.glob("scene_*.jpg"))) == 2


def test_scene_error_threshold_out_of_range(
    pymedia: Invoke,
    video_scenes: Path,
) -> None:
    """`scene` valida que el umbral esté en el rango permitido por Typer."""
    result = pymedia("scene", str(video_scenes), "--scene", "5")

    assert result.exit_code != 0
    assert "Invalid value for '--scene'" in result.output


def test_scene_success_with_range(
    pymedia: Invoke,
    video_scenes: Path,
    tmp_path: Path,
) -> None:
    """`scene --start --end` captura en el rango indicado."""
    output = tmp_path / "scene_range.jpg"

    result = pymedia(
        "scene",
        str(video_scenes),
        "-o",
        str(output),
        "-ov",
        "yes",
        "--start",
        "00:00:00",
        "--end",
        "00:00:02",
    )

    assert result.exit_code == 0
    assert len(list(tmp_path.glob("scene_range_*.jpg"))) >= 1


# =============================================================================
#  main (global)
# =============================================================================


def test_main_version(pymedia: Invoke) -> None:
    """`--version` muestra la versión de la aplicación."""
    result = pymedia("--version")

    assert result.exit_code == 0
    assert "Version" in result.output


def test_main_help(pymedia: Invoke) -> None:
    """`--help` muestra la ayuda global."""
    result = pymedia("--help")

    assert result.exit_code == 0
    # El nombre del programa difiere (`pyMedia` en CliRunner, `pymedia` en el
    # binario), así que se comprueba el texto de la ayuda, no el prog_name.
    assert "Usage:" in result.output
    assert "Easy CLI for ffmpeg" in result.output


# =============================================================================
#  end
# =============================================================================


def test_main_version_shows_runtime_details(pymedia: Invoke) -> None:
    """`--version` incluye la versión de Python y la plataforma."""
    result = pymedia("--version")

    assert result.exit_code == 0
    assert "Python:" in result.output
    assert "Platform:" in result.output


def test_main_without_arguments_shows_help(pymedia: Invoke) -> None:
    """`pymedia` sin argumentos muestra la ayuda global."""
    result = pymedia()

    # El código de salida (0 o 2) depende de la versión de Click.
    assert "Usage:" in result.output
    assert "Traceback" not in result.output


def test_hflip_changes_content(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`--hflip` produce una imagen con contenido espejado."""
    no_flip_path = tmp_path / "no_flip_h.jpg"
    hflip_path = tmp_path / "hflip_h.jpg"

    assert (
        pymedia(
            "frames",
            str(video_mp4_a),
            "--at",
            "00:00:01",
            "-o",
            str(no_flip_path),
            "-ov",
            "yes",
        ).exit_code
        == 0
    )
    assert (
        pymedia(
            "frames",
            str(video_mp4_a),
            "--at",
            "00:00:01",
            "-o",
            str(hflip_path),
            "-ov",
            "yes",
            "--hflip",
        ).exit_code
        == 0
    )

    generated = list(tmp_path.glob("no_flip_h_*.jpg"))
    assert generated
    no_flip_bytes = generated[0].read_bytes()
    generated = list(tmp_path.glob("hflip_h_*.jpg"))
    assert generated
    hflip_bytes = generated[0].read_bytes()

    assert no_flip_bytes != hflip_bytes


def test_vflip_changes_content(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`--vflip` produce una imagen con contenido verticalmente invertido."""
    no_flip_path = tmp_path / "no_flip_v.jpg"
    vflip_path = tmp_path / "vflip_v.jpg"

    assert (
        pymedia(
            "frames",
            str(video_mp4_a),
            "--at",
            "00:00:01",
            "-o",
            str(no_flip_path),
            "-ov",
            "yes",
        ).exit_code
        == 0
    )
    assert (
        pymedia(
            "frames",
            str(video_mp4_a),
            "--at",
            "00:00:01",
            "-o",
            str(vflip_path),
            "-ov",
            "yes",
            "--vflip",
        ).exit_code
        == 0
    )

    generated = list(tmp_path.glob("no_flip_v_*.jpg"))
    assert generated
    no_flip_bytes = generated[0].read_bytes()
    generated = list(tmp_path.glob("vflip_v_*.jpg"))
    assert generated
    vflip_bytes = generated[0].read_bytes()

    assert no_flip_bytes != vflip_bytes


def test_both_flip_changes_content(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`--hflip --vflip` produce una imagen volteada en ambos ejes."""
    no_flip_path = tmp_path / "no_flip_both.jpg"
    both_path = tmp_path / "both_flip.jpg"

    assert (
        pymedia(
            "frames",
            str(video_mp4_a),
            "--at",
            "00:00:01",
            "-o",
            str(no_flip_path),
            "-ov",
            "yes",
        ).exit_code
        == 0
    )
    assert (
        pymedia(
            "frames",
            str(video_mp4_a),
            "--at",
            "00:00:01",
            "-o",
            str(both_path),
            "-ov",
            "yes",
            "--hflip",
            "--vflip",
        ).exit_code
        == 0
    )

    generated = list(tmp_path.glob("no_flip_both_*.jpg"))
    assert generated
    no_flip_bytes = generated[0].read_bytes()
    generated = list(tmp_path.glob("both_flip_*.jpg"))
    assert generated
    both_bytes = generated[0].read_bytes()

    assert no_flip_bytes != both_bytes


def test_rotate_90_differs_from_270(
    pymedia: Invoke,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`--rotate 90` y `--rotate 270` producen resultados distintos."""
    r90_path = tmp_path / "rotate90.jpg"
    r270_path = tmp_path / "rotate270.jpg"

    assert (
        pymedia(
            "frames",
            str(video_mp4_a),
            "--at",
            "00:00:01",
            "-o",
            str(r90_path),
            "-ov",
            "yes",
            "--rotate",
            "90",
        ).exit_code
        == 0
    )
    assert (
        pymedia(
            "frames",
            str(video_mp4_a),
            "--at",
            "00:00:01",
            "-o",
            str(r270_path),
            "-ov",
            "yes",
            "--rotate",
            "270",
        ).exit_code
        == 0
    )

    generated = list(tmp_path.glob("rotate90_*.jpg"))
    assert generated
    r90_bytes = generated[0].read_bytes()
    generated = list(tmp_path.glob("rotate270_*.jpg"))
    assert generated
    r270_bytes = generated[0].read_bytes()

    assert r90_bytes != r270_bytes
