"""Tests end-to-end de la superficie Typer de la CLI de pyMedia.

Cada test invoca `pymedia.main.app` con `typer.testing.CliRunner` tal como lo
haría un usuario, comprobando el código de salida, los mensajes visibles y las
propiedades básicas de los ficheros generados (vía ffprobe). La lógica interna
de mixins y pipelines ya está cubierta por el resto de suites.
"""

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, cast

import pytest
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


def test_info_success_with_debug(runner: CliRunner, video_mp4_a: Path) -> None:
    """`info --debug` termina sin error mostrando los metadatos."""
    result = runner.invoke(app, ["info", str(video_mp4_a), "--debug"])

    assert result.exit_code == 0
    assert "Metadata" in result.output


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


def test_sheet_success_with_conflicting_name(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`sheet` dibuja el nombre aunque tenga `%`, comillas, comas o corchetes."""
    source = tmp_path / "100% real's, [2].mp4"
    shutil.copy(video_mp4_a, source)
    output = tmp_path / "sheet.jpg"

    result = runner.invoke(
        app,
        ["sheet", str(source), "-o", str(output), "--preset", "web"],
    )

    assert result.exit_code == 0
    assert output.exists()


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


def test_sheet_success_with_fhd_preset(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`sheet --preset fhd` genera una imagen jpg en resolución FHD."""
    output = tmp_path / "sheet_fhd.jpg"

    result = runner.invoke(
        app,
        ["sheet", str(video_mp4_a), "-o", str(output), "--preset", "fhd"],
    )

    assert result.exit_code == 0
    assert output.exists()


def test_sheet_success_with_overwrite_yes(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`sheet -ov yes` sobrescribe una imagen ya existente."""
    output = tmp_path / "sheet_overwrite.jpg"
    output.write_bytes(b"existing")

    result = runner.invoke(
        app,
        ["sheet", str(video_mp4_a), "-o", str(output), "-ov", "yes"],
    )

    assert result.exit_code == 0
    assert output.exists()
    assert output.read_bytes() != b"existing"


def test_sheet_error_overwrite_never(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`sheet -ov never` falla cuando el fichero ya existe."""
    output = tmp_path / "sheet_never.jpg"
    output.write_bytes(b"existing")

    result = runner.invoke(
        app,
        ["sheet", str(video_mp4_a), "-o", str(output), "-ov", "never"],
    )

    assert result.exit_code != 0


def test_sheet_success_with_directory(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`sheet --directory` genera la hoja dentro del directorio indicado."""
    directory = tmp_path / "sheets"

    result = runner.invoke(
        app,
        ["sheet", str(video_mp4_a), "--directory", str(directory), "--preset", "web"],
    )

    assert result.exit_code == 0
    generated = list(directory.glob("*_sheet.jpg"))
    assert len(generated) == 1


def test_sheet_success_multiple_inputs(
    runner: CliRunner,
    video_mp4_a: Path,
    video_mp4_b: Path,
    tmp_path: Path,
) -> None:
    """`sheet` con múltiples entradas y `--directory` genera una hoja por vídeo."""
    directory = tmp_path / "sheets"

    result = runner.invoke(
        app,
        [
            "sheet",
            str(video_mp4_a),
            str(video_mp4_b),
            "--directory",
            str(directory),
            "--preset",
            "web",
        ],
    )

    assert result.exit_code == 0
    generated = list(directory.glob("*_sheet.jpg"))
    assert len(generated) == 2


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


def test_join_success_with_overwrite_yes(
    runner: CliRunner,
    video_mp4_a: Path,
    video_mp4_b: Path,
    tmp_path: Path,
) -> None:
    """`join -ov yes` sobrescribe el fichero de salida existente."""
    output = tmp_path / "joined.mp4"
    output.write_bytes(b"existing")

    result = runner.invoke(
        app,
        ["join", str(video_mp4_a), str(video_mp4_b), "-o", str(output), "-ov", "yes"],
    )

    assert result.exit_code == 0
    assert output.exists()
    assert output.read_bytes() != b"existing"


def test_join_error_overwrite_never(
    runner: CliRunner,
    video_mp4_a: Path,
    video_mp4_b: Path,
    tmp_path: Path,
) -> None:
    """`join -ov never` falla cuando el fichero de salida ya existe."""
    output = tmp_path / "joined_never.mp4"
    output.write_bytes(b"existing")

    result = runner.invoke(
        app,
        ["join", str(video_mp4_a), str(video_mp4_b), "-o", str(output), "-ov", "never"],
    )

    assert result.exit_code != 0


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


def test_remux_success_with_genpts(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`remux --genpts` regenera los marcadores de tiempo."""
    output = tmp_path / "remuxed_genpts.mkv"

    result = runner.invoke(
        app,
        ["remux", str(video_mp4_a), "-o", str(output), "--genpts", "-ov", "yes"],
    )

    assert result.exit_code == 0
    assert output.exists()
    assert stream_types(output) == ["video", "audio"]


def test_remux_success_with_sort_tracks(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`remux --sort-tracks` ordena las pistas del contenedor."""
    output = tmp_path / "remuxed_sorted.mkv"

    result = runner.invoke(
        app,
        ["remux", str(video_mp4_a), "-o", str(output), "--sort-tracks", "-ov", "yes"],
    )

    assert result.exit_code == 0
    assert output.exists()
    assert stream_types(output) == ["video", "audio"]


def test_remux_error_overwrite_never(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`remux -ov never` falla cuando el fichero ya existe."""
    output = tmp_path / "remux_never.mkv"
    output.write_bytes(b"existing")

    result = runner.invoke(
        app,
        ["remux", str(video_mp4_a), "-o", str(output), "-ov", "never"],
    )

    assert result.exit_code != 0


def test_remux_error_change_incompatible_container(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`remux` rechaza cambiar a un contenedor incompatible con el códec."""
    output = tmp_path / "remuxed.webm"

    result = runner.invoke(
        app,
        ["remux", str(video_mp4_a), "-o", str(output), "-ov", "yes"],
    )

    assert result.exit_code != 0


# =============================================================================
#  cut
# =============================================================================


def test_cut_success_cuts_at_timestamp(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`cut --at` divide el vídeo en un segmento por cada marca."""
    output = tmp_path / "part.mp4"

    result = runner.invoke(
        app,
        [
            "cut",
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


def test_cut_error_missing_options(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`cut` exige una de `--at`, `--start` o `--end`."""
    result = runner.invoke(
        app,
        ["cut", str(video_mp4_a), "-o", str(tmp_path / "part.mp4")],
    )

    assert result.exit_code != 0
    normalized = " ".join(result.output.split())
    assert "Missing at least one of these options: at, start, end" in normalized


def test_cut_success_with_start(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`cut --start` divide el vídeo desde una marca hasta el final."""
    output = tmp_path / "from_start.mp4"

    result = runner.invoke(
        app,
        [
            "cut",
            str(video_mp4_a),
            "--start",
            "00:00:01",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    assert output.exists()
    assert ffprobe_duration(output) < 1.9


def test_cut_success_with_end(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`cut --end` divide el vídeo desde el inicio hasta una marca."""
    output = tmp_path / "from_end.mp4"

    result = runner.invoke(
        app,
        [
            "cut",
            str(video_mp4_a),
            "--end",
            "00:00:01",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    assert output.exists()
    assert ffprobe_duration(output) < 1.9


def test_cut_error_ambiguous_at_start(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`cut` rechaza combinar `--at` con `--start`."""
    result = runner.invoke(
        app,
        [
            "cut",
            str(video_mp4_a),
            "--at",
            "00:00:01",
            "--start",
            "00:00:00",
            "-o",
            str(tmp_path / "part.mp4"),
        ],
    )

    assert result.exit_code != 0
    assert "Ambiguous options" in result.output


def test_cut_error_ambiguous_at_end(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`cut` rechaza combinar `--at` con `--end`."""
    result = runner.invoke(
        app,
        [
            "cut",
            str(video_mp4_a),
            "--at",
            "00:00:01",
            "--end",
            "00:00:02",
            "-o",
            str(tmp_path / "part.mp4"),
        ],
    )

    assert result.exit_code != 0
    assert "Ambiguous options" in result.output


def test_cut_error_overwrite_never(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`cut -ov never` falla cuando el fichero ya existe."""
    output = tmp_path / "cut_never.mp4"
    output.write_bytes(b"existing")

    result = runner.invoke(
        app,
        [
            "cut",
            str(video_mp4_a),
            "--at",
            "00:00:01",
            "-o",
            str(output),
            "-ov",
            "never",
        ],
    )

    assert result.exit_code != 0


def test_cut_error_start_bigger_end(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`cut` rechaza `--start` posterior a `--end`."""
    result = runner.invoke(
        app,
        [
            "cut",
            str(video_mp4_a),
            "--start",
            "00:00:02",
            "--end",
            "00:00:01",
            "-o",
            str(tmp_path / "part.mp4"),
        ],
    )

    assert result.exit_code != 0


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


@pytest.mark.parametrize("name", ["Joan's first bycicle, [2].srt", "mi fichero.srt"])
def test_transcode_burns_subtitles_with_conflicting_name(
    runner: CliRunner,
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

    result = runner.invoke(
        app,
        [
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
    runner: CliRunner,
    audio_m4a: Path,
) -> None:
    """`transcode` rechaza ficheros de audio como entrada.

    Son contenedores inválidos para un comando que exige vídeo.
    """
    result = runner.invoke(
        app,
        [
            "transcode",
            str(audio_m4a),
            "--video",
            "-o",
            str(audio_m4a.parent / "out.mp4"),
        ],
    )

    assert result.exit_code != 0
    normalized = " ".join(result.output.split())
    assert "Invalid extension .m4a" in normalized
    assert "Video requires one of:" in normalized


def test_transcode_error_crop_bigger_than_video_dimensions(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`transcode --crop` rechaza área mayor que las dimensiones del vídeo."""
    output = tmp_path / "transcoded_crop.mp4"

    result = runner.invoke(
        app,
        [
            "transcode",
            str(video_mp4_a),
            "--crop",
            "160,90,10,10",
            "--video",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code != 0
    assert "Invalid crop area" in result.output


def test_transcode_error_oversize_without_upscale(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`transcode --size` mayor que el vídeo sin `--upscale` ignora el escalado."""
    output = tmp_path / "transcoded_oversize.mp4"

    result = runner.invoke(
        app,
        [
            "transcode",
            str(video_mp4_a),
            "--size",
            "320x180",
            "--video",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    assert "Ignored scale" in result.output


def test_transcode_success_with_preset_fast(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`transcode --preset fast` recodifica con el perfil fast."""
    output = tmp_path / "transcoded_fast.mp4"

    result = runner.invoke(
        app,
        [
            "transcode",
            str(video_mp4_a),
            "--preset",
            "fast",
            "--video",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    assert output.exists()


def test_transcode_success_transcode_audio(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`transcode --audio` recodifica la pista de audio."""
    output = tmp_path / "transcoded_audio.mp4"

    result = runner.invoke(
        app,
        [
            "transcode",
            str(video_mp4_a),
            "--audio",
            "0",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    assert output.exists()


def test_transcode_success_with_crop(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`transcode --crop` aplica recorte de imagen."""
    output = tmp_path / "transcoded_crop.mp4"

    result = runner.invoke(
        app,
        [
            "transcode",
            str(video_mp4_a),
            "--crop",
            "80,45,0,0",
            "--video",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    assert output.exists()


def test_transcode_success_with_rotate(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`transcode --rotate` rota la imagen 90 grados."""
    output = tmp_path / "transcoded_rotate.mp4"

    result = runner.invoke(
        app,
        [
            "transcode",
            str(video_mp4_a),
            "--rotate",
            "90",
            "--video",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    assert output.exists()


def test_transcode_success_with_size(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`transcode --size` escala la imagen a dimensiones objetivo."""
    output = tmp_path / "transcoded_size.mp4"

    result = runner.invoke(
        app,
        [
            "transcode",
            str(video_mp4_a),
            "--size",
            "128x72",
            "--video",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    assert output.exists()


def test_transcode_success_with_mode_stretch(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`transcode --mode stretch` escala modificando el aspect ratio."""
    output = tmp_path / "transcoded_mode.mp4"

    result = runner.invoke(
        app,
        [
            "transcode",
            str(video_mp4_a),
            "--mode",
            "stretch",
            "--video",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    assert output.exists()


def test_transcode_success_with_upscale(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`transcode --upscale` permite aumentar dimensiones."""
    output = tmp_path / "transcoded_upscale.mp4"

    result = runner.invoke(
        app,
        [
            "transcode",
            str(video_mp4_a),
            "--upscale",
            "--size",
            "320x180",
            "--video",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    assert output.exists()


def test_transcode_success_with_hflip(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`transcode --hflip` invierte la imagen horizontalmente."""
    output = tmp_path / "transcoded_hflip.mp4"

    result = runner.invoke(
        app,
        [
            "transcode",
            str(video_mp4_a),
            "--hflip",
            "--video",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    assert output.exists()


def test_transcode_success_with_vflip(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`transcode --vflip` invierte la imagen verticalmente."""
    output = tmp_path / "transcoded_vflip.mp4"

    result = runner.invoke(
        app,
        [
            "transcode",
            str(video_mp4_a),
            "--vflip",
            "--video",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    assert output.exists()


def test_transcode_error_overwrite_never(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`transcode -ov never` falla cuando el fichero ya existe."""
    output = tmp_path / "transcoded_never.mp4"
    output.write_bytes(b"existing")

    result = runner.invoke(
        app,
        ["transcode", str(video_mp4_a), "--video", "-o", str(output), "-ov", "never"],
    )

    assert result.exit_code != 0


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


def test_add_audio_success_with_title(
    runner: CliRunner,
    video_mkv: Path,
    audio_m4a: Path,
    tmp_path: Path,
) -> None:
    """`add-audio --title` añade título a la pista de audio."""
    output = tmp_path / "with_title.mkv"

    result = runner.invoke(
        app,
        [
            "add-audio",
            str(video_mkv),
            str(audio_m4a),
            "--language",
            "eng",
            "--title",
            "My Audio",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    audio_streams = [
        s for s in ffprobe_streams(output) if s.get("codec_type") == "audio"
    ]
    assert (audio_streams[-1].get("tags") or {}).get("title") == "My Audio"


def test_add_audio_success_with_forced(
    runner: CliRunner,
    video_mkv: Path,
    audio_m4a: Path,
    tmp_path: Path,
) -> None:
    """`add-audio --forced` marca la pista como forzada."""
    output = tmp_path / "with_forced.mkv"

    result = runner.invoke(
        app,
        [
            "add-audio",
            str(video_mkv),
            str(audio_m4a),
            "--language",
            "eng",
            "--forced",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    audio_streams = [
        s for s in ffprobe_streams(output) if s.get("codec_type") == "audio"
    ]
    assert audio_streams[-1].get("disposition", {}).get("forced") == 1


def test_add_audio_success_with_default(
    runner: CliRunner,
    video_mkv: Path,
    audio_m4a: Path,
    tmp_path: Path,
) -> None:
    """`add-audio --default` establece la pista como por defecto."""
    output = tmp_path / "with_default.mkv"

    result = runner.invoke(
        app,
        [
            "add-audio",
            str(video_mkv),
            str(audio_m4a),
            "--language",
            "eng",
            "--default",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    audio_streams = [
        s for s in ffprobe_streams(output) if s.get("codec_type") == "audio"
    ]
    assert audio_streams[-1].get("disposition", {}).get("default") == 1


def test_add_audio_success_with_hearing_impaired(
    runner: CliRunner,
    video_mkv: Path,
    audio_m4a: Path,
    tmp_path: Path,
) -> None:
    """`add-audio --hearing-impaired` marca pista para discapacitados auditivos."""
    output = tmp_path / "with_hi.mkv"

    result = runner.invoke(
        app,
        [
            "add-audio",
            str(video_mkv),
            str(audio_m4a),
            "--language",
            "eng",
            "--hearing-impaired",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    audio_streams = [
        s for s in ffprobe_streams(output) if s.get("codec_type") == "audio"
    ]
    assert audio_streams[-1].get("disposition", {}).get("hearing_impaired") == 1


def test_add_audio_success_with_commentary(
    runner: CliRunner,
    video_mkv: Path,
    audio_m4a: Path,
    tmp_path: Path,
) -> None:
    """`add-audio --commentary` marca la pista como comentario."""
    output = tmp_path / "with_commentary.mkv"

    result = runner.invoke(
        app,
        [
            "add-audio",
            str(video_mkv),
            str(audio_m4a),
            "--language",
            "eng",
            "--commentary",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    audio_streams = [
        s for s in ffprobe_streams(output) if s.get("codec_type") == "audio"
    ]
    assert audio_streams[-1].get("disposition", {}).get("comment") == 1


def test_add_audio_error_overwrite_never(
    runner: CliRunner,
    video_mkv: Path,
    audio_m4a: Path,
    tmp_path: Path,
) -> None:
    """`add-audio -ov never` falla cuando el fichero ya existe."""
    output = tmp_path / "audio_never.mkv"
    output.write_bytes(b"existing")

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
            "never",
        ],
    )

    assert result.exit_code != 0


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
            "--tracks",
            "0",
            "-o",
            str(tmp_path / "out.mp4"),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code != 0
    assert "Missing parameter: media.audio" in result.output


def test_delete_audio_error_overwrite_never(
    runner: CliRunner,
    video_mkv: Path,
    tmp_path: Path,
) -> None:
    """`delete-audio -ov never` falla cuando el fichero ya existe."""
    output = tmp_path / "no_audio_never.mkv"
    output.write_bytes(b"existing")

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
            "never",
        ],
    )

    assert result.exit_code != 0


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


def test_edit_audio_success_with_title(
    runner: CliRunner,
    video_mkv: Path,
    tmp_path: Path,
) -> None:
    """`edit-audio --title` actualiza el título de la pista."""
    output = tmp_path / "edited_title.mkv"

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
            "French Audio",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    assert stream_tag(output, "audio", "title") == "French Audio"


def test_edit_audio_success_with_forced(
    runner: CliRunner,
    video_mkv: Path,
    tmp_path: Path,
) -> None:
    """`edit-audio --forced` marca la pista como forzada."""
    output = tmp_path / "edited_forced.mkv"

    result = runner.invoke(
        app,
        [
            "edit-audio",
            str(video_mkv),
            "--track",
            "0",
            "--language",
            "fre",
            "--forced",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    assert stream_tag(output, "audio", "language") == "fre"
    assert ffprobe_streams(output)[1].get("disposition", {}).get("forced") == 1


def test_edit_audio_success_with_default(
    runner: CliRunner,
    video_mkv: Path,
    tmp_path: Path,
) -> None:
    """`edit-audio --default` establece la pista como por defecto."""
    output = tmp_path / "edited_default.mkv"

    result = runner.invoke(
        app,
        [
            "edit-audio",
            str(video_mkv),
            "--track",
            "0",
            "--language",
            "fre",
            "--default",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    assert stream_tag(output, "audio", "language") == "fre"
    assert ffprobe_streams(output)[1].get("disposition", {}).get("default") == 1


def test_edit_audio_success_with_hearing_impaired(
    runner: CliRunner,
    video_mkv: Path,
    tmp_path: Path,
) -> None:
    """`edit-audio --hearing-impaired` marca pista para discapacitados auditivos."""
    output = tmp_path / "edited_hi.mkv"

    result = runner.invoke(
        app,
        [
            "edit-audio",
            str(video_mkv),
            "--track",
            "0",
            "--language",
            "fre",
            "--hearing-impaired",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    assert stream_tag(output, "audio", "language") == "fre"
    assert (
        ffprobe_streams(output)[1].get("disposition", {}).get("hearing_impaired") == 1
    )


def test_edit_audio_success_with_commentary(
    runner: CliRunner,
    video_mkv: Path,
    tmp_path: Path,
) -> None:
    """`edit-audio --commentary` marca la pista como comentario."""
    output = tmp_path / "edited_commentary.mkv"

    result = runner.invoke(
        app,
        [
            "edit-audio",
            str(video_mkv),
            "--track",
            "0",
            "--language",
            "fre",
            "--commentary",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    assert stream_tag(output, "audio", "language") == "fre"
    assert ffprobe_streams(output)[1].get("disposition", {}).get("comment") == 1


def test_edit_audio_error_missing_metadata(
    runner: CliRunner,
    video_mkv: Path,
) -> None:
    """`edit-audio` exige al menos una opción de metadatos."""
    result = runner.invoke(
        app,
        [
            "edit-audio",
            str(video_mkv),
            "--track",
            "0",
        ],
    )

    assert result.exit_code != 0
    normalized = " ".join(result.output.split())
    assert "Missing at least one of these options:" in normalized


def test_edit_audio_error_overwrite_never(
    runner: CliRunner,
    video_mkv: Path,
    tmp_path: Path,
) -> None:
    """`edit-audio -ov never` falla cuando el fichero ya existe."""
    output = tmp_path / "edited_never.mkv"
    output.write_bytes(b"existing")

    result = runner.invoke(
        app,
        [
            "edit-audio",
            str(video_mkv),
            "--track",
            "0",
            "--language",
            "fre",
            "-o",
            str(output),
            "-ov",
            "never",
        ],
    )

    assert result.exit_code != 0


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
    result = runner.invoke(
        app,
        ["extract-audio", str(video_no_audio), "--tracks", "0"],
    )

    assert result.exit_code != 0
    assert "Missing parameter: media.audio" in result.output


def test_extract_audio_error_overwrite_never(
    runner: CliRunner,
    video_mkv: Path,
    tmp_path: Path,
) -> None:
    """`extract-audio -ov never` falla cuando el fichero ya existe."""
    output = tmp_path / "audio_never.m4a"
    output.write_bytes(b"existing")

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
            "never",
        ],
    )

    assert result.exit_code != 0


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
    # El mensaje de ffprobe puede partirse en varias líneas con espacios extra
    output = " ".join(result.output.split())
    assert "Invalid data found" in output
    assert "when processing input" in output


def test_add_subs_success_with_title(
    runner: CliRunner,
    video_mkv: Path,
    subs_spa: Path,
    tmp_path: Path,
) -> None:
    """`add-subs --title` añade título a la pista de subtítulos."""
    output = tmp_path / "with_title.mkv"

    result = runner.invoke(
        app,
        [
            "add-subs",
            str(video_mkv),
            str(subs_spa),
            "--language",
            "spa",
            "--title",
            "Spanish subs",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    assert stream_tag(output, "subtitle", "title") == "Spanish subs"


def test_add_subs_success_with_forced(
    runner: CliRunner,
    video_mkv: Path,
    subs_spa: Path,
    tmp_path: Path,
) -> None:
    """`add-subs --forced` marca la pista como forzada."""
    output = tmp_path / "with_forced.mkv"

    result = runner.invoke(
        app,
        [
            "add-subs",
            str(video_mkv),
            str(subs_spa),
            "--language",
            "spa",
            "--forced",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    sub_streams = [
        s for s in ffprobe_streams(output) if s.get("codec_type") == "subtitle"
    ]
    assert sub_streams[-1].get("disposition", {}).get("forced") == 1


def test_add_subs_success_with_default(
    runner: CliRunner,
    video_mkv: Path,
    subs_spa: Path,
    tmp_path: Path,
) -> None:
    """`add-subs --default` establece la pista como por defecto."""
    output = tmp_path / "with_default.mkv"

    result = runner.invoke(
        app,
        [
            "add-subs",
            str(video_mkv),
            str(subs_spa),
            "--language",
            "spa",
            "--default",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    sub_streams = [
        s for s in ffprobe_streams(output) if s.get("codec_type") == "subtitle"
    ]
    assert sub_streams[-1].get("disposition", {}).get("default") == 1


def test_add_subs_success_with_hearing_impaired(
    runner: CliRunner,
    video_mkv: Path,
    subs_spa: Path,
    tmp_path: Path,
) -> None:
    """`add-subs --hearing-impaired` marca pista para discapacitados auditivos."""
    output = tmp_path / "with_hi.mkv"

    result = runner.invoke(
        app,
        [
            "add-subs",
            str(video_mkv),
            str(subs_spa),
            "--language",
            "spa",
            "--hearing-impaired",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    sub_streams = [
        s for s in ffprobe_streams(output) if s.get("codec_type") == "subtitle"
    ]
    assert sub_streams[-1].get("disposition", {}).get("hearing_impaired") == 1


def test_add_subs_success_with_visual_impaired(
    runner: CliRunner,
    video_mkv: Path,
    subs_spa: Path,
    tmp_path: Path,
) -> None:
    """`add-subs --visual-impaired` marca pista para discapacitados visuales."""
    output = tmp_path / "with_visual.mkv"

    result = runner.invoke(
        app,
        [
            "add-subs",
            str(video_mkv),
            str(subs_spa),
            "--language",
            "spa",
            "--visual-impaired",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    sub_streams = [
        s for s in ffprobe_streams(output) if s.get("codec_type") == "subtitle"
    ]
    assert sub_streams[-1].get("disposition", {}).get("visual_impaired") == 1


def test_add_subs_error_overwrite_never(
    runner: CliRunner,
    video_mkv: Path,
    subs_spa: Path,
    tmp_path: Path,
) -> None:
    """`add-subs -ov never` falla cuando el fichero ya existe."""
    output = tmp_path / "subs_never.mkv"
    output.write_bytes(b"existing")

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
            "never",
        ],
    )

    assert result.exit_code != 0


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
        [
            "delete-subs",
            str(video_mkv),
            "--tracks",
            "0",
            "-o",
            str(tmp_path / "out.mkv"),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code != 0
    assert "Missing parameter: media.subtitles" in result.output


def test_delete_subs_success_multiple_tracks(
    runner: CliRunner,
    video_mkv_subs: Path,
    tmp_path: Path,
) -> None:
    """`delete-subs --tracks 0,1` elimina ambas pistas de subtítulos."""
    output = tmp_path / "no_subs.mkv"

    result = runner.invoke(
        app,
        [
            "delete-subs",
            str(video_mkv_subs),
            "--tracks",
            "0,1",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    assert "subtitle" not in stream_types(output)


def test_delete_subs_error_overwrite_never(
    runner: CliRunner,
    video_mkv_subs: Path,
    tmp_path: Path,
) -> None:
    """`delete-subs -ov never` falla cuando el fichero ya existe."""
    output = tmp_path / "subs_never.mkv"
    output.write_bytes(b"existing")

    result = runner.invoke(
        app,
        [
            "delete-subs",
            str(video_mkv_subs),
            "--tracks",
            "0",
            "-o",
            str(output),
            "-ov",
            "never",
        ],
    )

    assert result.exit_code != 0


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


def test_edit_subs_success_with_title(
    runner: CliRunner,
    video_mkv_subs: Path,
    tmp_path: Path,
) -> None:
    """`edit-subs --title` actualiza el título de la pista."""
    output = tmp_path / "edited_title.mkv"

    result = runner.invoke(
        app,
        [
            "edit-subs",
            str(video_mkv_subs),
            "--track",
            "0",
            "--language",
            "fre",
            "--title",
            "French Subs",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    assert stream_tag(output, "subtitle", "title") == "French Subs"


def test_edit_subs_success_with_forced(
    runner: CliRunner,
    video_mkv_subs: Path,
    tmp_path: Path,
) -> None:
    """`edit-subs --forced` marca la pista como forzada."""
    output = tmp_path / "edited_forced.mkv"

    result = runner.invoke(
        app,
        [
            "edit-subs",
            str(video_mkv_subs),
            "--track",
            "0",
            "--language",
            "fre",
            "--forced",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    assert stream_tag(output, "subtitle", "language") == "fre"
    sub = next(s for s in ffprobe_streams(output) if s.get("codec_type") == "subtitle")
    assert sub.get("disposition", {}).get("forced") == 1


def test_edit_subs_success_with_default(
    runner: CliRunner,
    video_mkv_subs: Path,
    tmp_path: Path,
) -> None:
    """`edit-subs --default` establece la pista como por defecto."""
    output = tmp_path / "edited_default.mkv"

    result = runner.invoke(
        app,
        [
            "edit-subs",
            str(video_mkv_subs),
            "--track",
            "0",
            "--language",
            "fre",
            "--default",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    assert stream_tag(output, "subtitle", "language") == "fre"
    sub = next(s for s in ffprobe_streams(output) if s.get("codec_type") == "subtitle")
    assert sub.get("disposition", {}).get("default") == 1


def test_edit_subs_success_with_hearing_impaired(
    runner: CliRunner,
    video_mkv_subs: Path,
    tmp_path: Path,
) -> None:
    """`edit-subs --hearing-impaired` marca pista para discapacitados auditivos."""
    output = tmp_path / "edited_hi.mkv"

    result = runner.invoke(
        app,
        [
            "edit-subs",
            str(video_mkv_subs),
            "--track",
            "0",
            "--language",
            "fre",
            "--hearing-impaired",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    assert stream_tag(output, "subtitle", "language") == "fre"
    sub = next(s for s in ffprobe_streams(output) if s.get("codec_type") == "subtitle")
    assert sub.get("disposition", {}).get("hearing_impaired") == 1


def test_edit_subs_success_with_visual_impaired(
    runner: CliRunner,
    video_mkv_subs: Path,
    tmp_path: Path,
) -> None:
    """`edit-subs --visual-impaired` marca pista para discapacitados visuales."""
    output = tmp_path / "edited_visual.mkv"

    result = runner.invoke(
        app,
        [
            "edit-subs",
            str(video_mkv_subs),
            "--track",
            "0",
            "--language",
            "fre",
            "--visual-impaired",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    assert stream_tag(output, "subtitle", "language") == "fre"
    sub = next(s for s in ffprobe_streams(output) if s.get("codec_type") == "subtitle")
    assert sub.get("disposition", {}).get("visual_impaired") == 1


def test_edit_subs_error_missing_metadata(
    runner: CliRunner,
    video_mkv_subs: Path,
) -> None:
    """`edit-subs` exige al menos una opción de metadatos."""
    result = runner.invoke(
        app,
        [
            "edit-subs",
            str(video_mkv_subs),
            "--track",
            "0",
        ],
    )

    assert result.exit_code != 0
    normalized = " ".join(result.output.split())
    assert "Missing at least one of these options:" in normalized


def test_edit_subs_error_overwrite_never(
    runner: CliRunner,
    video_mkv_subs: Path,
    tmp_path: Path,
) -> None:
    """`edit-subs -ov never` falla cuando el fichero ya existe."""
    output = tmp_path / "edited_never.mkv"
    output.write_bytes(b"existing")

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
            "never",
        ],
    )

    assert result.exit_code != 0


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


def test_extract_subs_success_multiple_tracks(
    runner: CliRunner,
    video_mkv_subs: Path,
    tmp_path: Path,
) -> None:
    """`extract-subs --tracks 0,1` extrae ambas pistas de subtítulos."""
    output = tmp_path / "subs.srt"

    result = runner.invoke(
        app,
        [
            "extract-subs",
            str(video_mkv_subs),
            "--tracks",
            "0,1",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code == 0
    extracted = list(tmp_path.glob("subs_subtitles_track_*.srt"))
    assert len(extracted) == 2


def test_extract_subs_error_overwrite_never(
    runner: CliRunner,
    video_mkv_subs: Path,
    tmp_path: Path,
) -> None:
    """`extract-subs -ov never` falla cuando el fichero ya existe."""
    output = tmp_path / "subs.srt"
    output.write_text("existing", encoding="utf-8")

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
            "never",
        ],
    )

    assert result.exit_code != 0


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


def test_animated_success_with_range(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`animated --start --end` genera gif limitado al rango."""
    output = tmp_path / "anim_range.gif"

    result = runner.invoke(
        app,
        [
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
        ],
    )

    assert result.exit_code == 0
    assert output.exists()


def test_animated_success_with_fps_15(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`animated --fps 15` genera gif a 15 fps."""
    output = tmp_path / "anim_fps15.gif"

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
            "15",
        ],
    )

    assert result.exit_code == 0
    assert output.exists()


def test_animated_error_fps_out_of_range(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`animated --fps 3` rechaza fps fuera del rango."""
    result = runner.invoke(
        app,
        ["animated", str(video_mp4_a), "-o", str(tmp_path / "anim.gif"), "--fps", "3"],
    )

    assert result.exit_code != 0
    assert "Invalid value for '--fps'" in result.output


def test_animated_success_with_crop(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`animated --crop` aplica recorte."""
    output = tmp_path / "anim_crop.gif"

    result = runner.invoke(
        app,
        [
            "animated",
            str(video_mp4_a),
            "-o",
            str(output),
            "-ov",
            "yes",
            "--crop",
            "80,45,0,0",
        ],
    )

    assert result.exit_code == 0
    assert output.exists()


def test_animated_success_with_rotate(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`animated --rotate` rota la imagen."""
    output = tmp_path / "anim_rotate.gif"

    result = runner.invoke(
        app,
        [
            "animated",
            str(video_mp4_a),
            "-o",
            str(output),
            "-ov",
            "yes",
            "--rotate",
            "90",
        ],
    )

    assert result.exit_code == 0
    assert output.exists()


def test_animated_success_with_size(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`animated --size` cambia la resolución."""
    output = tmp_path / "anim_size.gif"

    result = runner.invoke(
        app,
        [
            "animated",
            str(video_mp4_a),
            "-o",
            str(output),
            "-ov",
            "yes",
            "--size",
            "320x180",
        ],
    )

    assert result.exit_code == 0
    assert output.exists()


def test_animated_success_with_mode_stretch(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`animated --mode stretch` escala modificando aspect ratio."""
    output = tmp_path / "anim_mode.gif"

    result = runner.invoke(
        app,
        [
            "animated",
            str(video_mp4_a),
            "-o",
            str(output),
            "-ov",
            "yes",
            "--mode",
            "stretch",
        ],
    )

    assert result.exit_code == 0
    assert output.exists()


def test_animated_success_with_upscale(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`animated --upscale` permite aumentar dimensiones."""
    output = tmp_path / "anim_upscale.gif"

    result = runner.invoke(
        app,
        [
            "animated",
            str(video_mp4_a),
            "-o",
            str(output),
            "-ov",
            "yes",
            "--upscale",
            "--size",
            "640x360",
        ],
    )

    assert result.exit_code == 0
    assert output.exists()


def test_animated_success_with_hflip(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`animated --hflip` invierte horizontalmente."""
    output = tmp_path / "anim_hflip.gif"

    result = runner.invoke(
        app,
        [
            "animated",
            str(video_mp4_a),
            "-o",
            str(output),
            "-ov",
            "yes",
            "--hflip",
        ],
    )

    assert result.exit_code == 0
    assert output.exists()


def test_animated_success_with_vflip(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`animated --vflip` invierte verticalmente."""
    output = tmp_path / "anim_vflip.gif"

    result = runner.invoke(
        app,
        [
            "animated",
            str(video_mp4_a),
            "-o",
            str(output),
            "-ov",
            "yes",
            "--vflip",
        ],
    )

    assert result.exit_code == 0
    assert output.exists()


def test_animated_error_overwrite_never(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`animated -ov never` falla cuando el fichero ya existe."""
    output = tmp_path / "anim_never.gif"
    output.write_bytes(b"existing")

    result = runner.invoke(
        app,
        ["animated", str(video_mp4_a), "-o", str(output), "-ov", "never"],
    )

    assert result.exit_code != 0


def test_animated_error_crop_bigger_than_video_dimensions(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`animated --crop` rechaza área mayor que las dimensiones del vídeo."""
    output = tmp_path / "anim_crop.gif"

    result = runner.invoke(
        app,
        [
            "animated",
            str(video_mp4_a),
            "-o",
            str(output),
            "-ov",
            "yes",
            "--crop",
            "160,90,10,10",
        ],
    )

    assert result.exit_code != 0
    assert "Invalid crop area" in result.output


def test_animated_error_oversize_without_upscale(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`animated --size` mayor que el vídeo sin `--upscale` ignora el escalado."""
    output = tmp_path / "anim_oversize.gif"

    result = runner.invoke(
        app,
        [
            "animated",
            str(video_mp4_a),
            "-o",
            str(output),
            "-ov",
            "yes",
            "--size",
            "320x180",
        ],
    )

    assert result.exit_code == 0
    assert "Ignored scale" in result.output


def test_animated_error_timestamp_bigger_than_video_duration(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`animated --start` rechaza marca de tiempo mayor que la duración."""
    output = tmp_path / "anim_timestamp.gif"

    result = runner.invoke(
        app,
        [
            "animated",
            str(video_mp4_a),
            "-o",
            str(output),
            "-ov",
            "yes",
            "--start",
            "00:00:03",
        ],
    )

    assert result.exit_code != 0
    assert "exceeds video duration" in result.output


def test_animated_success_generates_apng(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`animated -o output.apng` genera una imagen APNG."""
    output = tmp_path / "anim.apng"

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
        ],
    )

    assert result.exit_code == 0
    assert output.exists()
    assert stream_codec_names(output, "video") == ["apng"]


def test_animated_success_generates_webp(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`animated -o output.webp` genera una imagen WebP animada."""
    output = tmp_path / "anim.webp"

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
        ],
    )

    assert result.exit_code == 0
    assert output.exists()


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


def test_frames_success_with_crop(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`frames --crop` aplica recorte a la miniatura."""
    output = tmp_path / "thumb_crop.jpg"

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
            "--crop",
            "80,45,0,0",
        ],
    )

    assert result.exit_code == 0
    assert len(list(tmp_path.glob("thumb_crop_*.jpg"))) == 1


def test_frames_success_with_rotate(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`frames --rotate` rota la miniatura."""
    output = tmp_path / "thumb_rotate.jpg"

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
            "--rotate",
            "90",
        ],
    )

    assert result.exit_code == 0
    assert len(list(tmp_path.glob("thumb_rotate_*.jpg"))) == 1


def test_frames_success_with_size(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`frames --size` cambia la resolución de la miniatura."""
    output = tmp_path / "thumb_size.jpg"

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
            "--size",
            "128x72",
        ],
    )

    assert result.exit_code == 0
    assert len(list(tmp_path.glob("thumb_size_*.jpg"))) == 1


def test_frames_success_with_mode_stretch(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`frames --mode stretch` escala modificando aspect ratio."""
    output = tmp_path / "thumb_mode.jpg"

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
            "--mode",
            "stretch",
        ],
    )

    assert result.exit_code == 0
    assert len(list(tmp_path.glob("thumb_mode_*.jpg"))) == 1


def test_frames_success_with_upscale(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`frames --upscale` permite aumentar dimensiones."""
    output = tmp_path / "thumb_upscale.jpg"

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
            "--upscale",
            "--size",
            "320x180",
        ],
    )

    assert result.exit_code == 0
    assert len(list(tmp_path.glob("thumb_upscale_*.jpg"))) == 1


def test_frames_success_with_hflip(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`frames --hflip` invierte horizontalmente."""
    output = tmp_path / "thumb_hflip.jpg"

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
            "--hflip",
        ],
    )

    assert result.exit_code == 0
    assert len(list(tmp_path.glob("thumb_hflip_*.jpg"))) == 1


def test_frames_success_with_vflip(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`frames --vflip` invierte verticalmente."""
    output = tmp_path / "thumb_vflip.jpg"

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
            "--vflip",
        ],
    )

    assert result.exit_code == 0
    assert len(list(tmp_path.glob("thumb_vflip_*.jpg"))) == 1


def test_frames_error_overwrite_never(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`frames -ov never` falla cuando el fichero ya existe."""
    output = tmp_path / "thumb_never.jpg"
    output.write_bytes(b"existing")

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
            "never",
        ],
    )

    assert result.exit_code != 0


def test_frames_error_crop_bigger_than_video_dimensions(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`frames --crop` rechaza área mayor que las dimensiones del vídeo."""
    output = tmp_path / "frames_crop.jpg"

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
            "--crop",
            "160,90,10,10",
        ],
    )

    assert result.exit_code != 0
    assert "Invalid crop area" in result.output


def test_frames_error_oversize_without_upscale(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`frames --size` mayor que el vídeo sin `--upscale` ignora el escalado."""
    output = tmp_path / "frames_oversize.jpg"

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
            "--size",
            "320x180",
        ],
    )

    assert result.exit_code == 0
    assert "Ignored scale" in result.output


def test_frames_error_timestamp_bigger_than_video_duration(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`frames --at` rechaza marca de tiempo mayor que la duración."""
    output = tmp_path / "frames_timestamp.jpg"

    result = runner.invoke(
        app,
        [
            "frames",
            str(video_mp4_a),
            "--at",
            "00:00:03",
            "-o",
            str(output),
            "-ov",
            "yes",
        ],
    )

    assert result.exit_code != 0
    assert "exceeds video duration" in result.output


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


def test_interval_success_with_range(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`interval --start --end` genera miniaturas en el rango indicado."""
    output = tmp_path / "periodic_range.jpg"

    result = runner.invoke(
        app,
        [
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
        ],
    )

    assert result.exit_code == 0
    assert len(list(tmp_path.glob("periodic_range_*.jpg"))) >= 1


def test_interval_error_every_too_small(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`interval --every 0` rechaza periodo menor a 1 segundo."""
    result = runner.invoke(
        app,
        ["interval", str(video_mp4_a), "--every", "0", "-o", str(tmp_path / "p.jpg")],
    )

    assert result.exit_code != 0
    assert "Interval must be at least 1 second" in result.output


def test_interval_success_with_crop(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`interval --crop` aplica recorte."""
    output = tmp_path / "periodic_crop.jpg"

    result = runner.invoke(
        app,
        [
            "interval",
            str(video_mp4_a),
            "--every",
            "1",
            "-o",
            str(output),
            "-ov",
            "yes",
            "--crop",
            "80,45,0,0",
        ],
    )

    assert result.exit_code == 0
    assert len(list(tmp_path.glob("periodic_crop_*.jpg"))) >= 1


def test_interval_success_with_rotate(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`interval --rotate` rota las miniaturas."""
    output = tmp_path / "periodic_rotate.jpg"

    result = runner.invoke(
        app,
        [
            "interval",
            str(video_mp4_a),
            "--every",
            "1",
            "-o",
            str(output),
            "-ov",
            "yes",
            "--rotate",
            "90",
        ],
    )

    assert result.exit_code == 0
    assert len(list(tmp_path.glob("periodic_rotate_*.jpg"))) >= 1


def test_interval_success_with_size(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`interval --size` cambia la resolución."""
    output = tmp_path / "periodic_size.jpg"

    result = runner.invoke(
        app,
        [
            "interval",
            str(video_mp4_a),
            "--every",
            "1",
            "-o",
            str(output),
            "-ov",
            "yes",
            "--size",
            "128x72",
        ],
    )

    assert result.exit_code == 0
    assert len(list(tmp_path.glob("periodic_size_*.jpg"))) >= 1


def test_interval_success_with_mode_stretch(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`interval --mode stretch` escala modificando aspect ratio."""
    output = tmp_path / "periodic_mode.jpg"

    result = runner.invoke(
        app,
        [
            "interval",
            str(video_mp4_a),
            "--every",
            "1",
            "-o",
            str(output),
            "-ov",
            "yes",
            "--mode",
            "stretch",
        ],
    )

    assert result.exit_code == 0
    assert len(list(tmp_path.glob("periodic_mode_*.jpg"))) >= 1


def test_interval_success_with_upscale(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`interval --upscale` permite aumentar dimensiones."""
    output = tmp_path / "periodic_upscale.jpg"

    result = runner.invoke(
        app,
        [
            "interval",
            str(video_mp4_a),
            "--every",
            "1",
            "-o",
            str(output),
            "-ov",
            "yes",
            "--upscale",
            "--size",
            "320x180",
        ],
    )

    assert result.exit_code == 0
    assert len(list(tmp_path.glob("periodic_upscale_*.jpg"))) >= 1


def test_interval_success_with_hflip(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`interval --hflip` invierte horizontalmente."""
    output = tmp_path / "periodic_hflip.jpg"

    result = runner.invoke(
        app,
        [
            "interval",
            str(video_mp4_a),
            "--every",
            "1",
            "-o",
            str(output),
            "-ov",
            "yes",
            "--hflip",
        ],
    )

    assert result.exit_code == 0
    assert len(list(tmp_path.glob("periodic_hflip_*.jpg"))) >= 1


def test_interval_success_with_vflip(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`interval --vflip` invierte verticalmente."""
    output = tmp_path / "periodic_vflip.jpg"

    result = runner.invoke(
        app,
        [
            "interval",
            str(video_mp4_a),
            "--every",
            "1",
            "-o",
            str(output),
            "-ov",
            "yes",
            "--vflip",
        ],
    )

    assert result.exit_code == 0
    assert len(list(tmp_path.glob("periodic_vflip_*.jpg"))) >= 1


def test_interval_error_overwrite_never(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`interval -ov never` falla cuando el fichero ya existe."""
    output = tmp_path / "periodic_never.jpg"
    output.write_bytes(b"existing")

    result = runner.invoke(
        app,
        [
            "interval",
            str(video_mp4_a),
            "--every",
            "1",
            "-o",
            str(output),
            "-ov",
            "never",
        ],
    )

    assert result.exit_code != 0


def test_interval_error_crop_bigger_than_video_dimensions(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`interval --crop` rechaza área mayor que las dimensiones del vídeo."""
    output = tmp_path / "periodic_crop.jpg"

    result = runner.invoke(
        app,
        [
            "interval",
            str(video_mp4_a),
            "--every",
            "1",
            "-o",
            str(output),
            "-ov",
            "yes",
            "--crop",
            "160,90,10,10",
        ],
    )

    assert result.exit_code != 0
    assert "Invalid crop area" in result.output


def test_interval_error_oversize_without_upscale(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`interval --size` mayor que el vídeo sin `--upscale` ignora el escalado."""
    output = tmp_path / "periodic_oversize.jpg"

    result = runner.invoke(
        app,
        [
            "interval",
            str(video_mp4_a),
            "--every",
            "1",
            "-o",
            str(output),
            "-ov",
            "yes",
            "--size",
            "320x180",
        ],
    )

    assert result.exit_code == 0
    assert "Ignored scale" in result.output


def test_interval_error_timestamp_bigger_than_video_duration(
    runner: CliRunner,
    video_mp4_a: Path,
    tmp_path: Path,
) -> None:
    """`interval --start` rechaza marca de tiempo mayor que la duración."""
    output = tmp_path / "periodic_timestamp.jpg"

    result = runner.invoke(
        app,
        [
            "interval",
            str(video_mp4_a),
            "--every",
            "1",
            "-o",
            str(output),
            "-ov",
            "yes",
            "--start",
            "00:00:03",
        ],
    )

    assert result.exit_code != 0
    assert "exceeds video duration" in result.output


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


def test_scene_success_with_range(
    runner: CliRunner,
    video_scenes: Path,
    tmp_path: Path,
) -> None:
    """`scene --start --end` captura en el rango indicado."""
    output = tmp_path / "scene_range.jpg"

    result = runner.invoke(
        app,
        [
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
        ],
    )

    assert result.exit_code == 0
    assert len(list(tmp_path.glob("scene_range_*.jpg"))) >= 1


def test_scene_success_with_crop(
    runner: CliRunner,
    video_scenes: Path,
    tmp_path: Path,
) -> None:
    """`scene --crop` aplica recorte."""
    output = tmp_path / "scene_crop.jpg"

    result = runner.invoke(
        app,
        [
            "scene",
            str(video_scenes),
            "-o",
            str(output),
            "-ov",
            "yes",
            "--crop",
            "80,45,0,0",
        ],
    )

    assert result.exit_code == 0
    assert len(list(tmp_path.glob("scene_crop_*.jpg"))) >= 1


def test_scene_success_with_rotate(
    runner: CliRunner,
    video_scenes: Path,
    tmp_path: Path,
) -> None:
    """`scene --rotate` rota las capturas."""
    output = tmp_path / "scene_rotate.jpg"

    result = runner.invoke(
        app,
        [
            "scene",
            str(video_scenes),
            "-o",
            str(output),
            "-ov",
            "yes",
            "--rotate",
            "90",
        ],
    )

    assert result.exit_code == 0
    assert len(list(tmp_path.glob("scene_rotate_*.jpg"))) >= 1


def test_scene_success_with_size(
    runner: CliRunner,
    video_scenes: Path,
    tmp_path: Path,
) -> None:
    """`scene --size` cambia la resolución."""
    output = tmp_path / "scene_size.jpg"

    result = runner.invoke(
        app,
        [
            "scene",
            str(video_scenes),
            "-o",
            str(output),
            "-ov",
            "yes",
            "--size",
            "128x72",
        ],
    )

    assert result.exit_code == 0
    assert len(list(tmp_path.glob("scene_size_*.jpg"))) >= 1


def test_scene_success_with_mode_stretch(
    runner: CliRunner,
    video_scenes: Path,
    tmp_path: Path,
) -> None:
    """`scene --mode stretch` escala modificando aspect ratio."""
    output = tmp_path / "scene_mode.jpg"

    result = runner.invoke(
        app,
        [
            "scene",
            str(video_scenes),
            "-o",
            str(output),
            "-ov",
            "yes",
            "--mode",
            "stretch",
        ],
    )

    assert result.exit_code == 0
    assert len(list(tmp_path.glob("scene_mode_*.jpg"))) >= 1


def test_scene_success_with_upscale(
    runner: CliRunner,
    video_scenes: Path,
    tmp_path: Path,
) -> None:
    """`scene --upscale` permite aumentar dimensiones."""
    output = tmp_path / "scene_upscale.jpg"

    result = runner.invoke(
        app,
        [
            "scene",
            str(video_scenes),
            "-o",
            str(output),
            "-ov",
            "yes",
            "--upscale",
            "--size",
            "320x180",
        ],
    )

    assert result.exit_code == 0
    assert len(list(tmp_path.glob("scene_upscale_*.jpg"))) >= 1


def test_scene_success_with_hflip(
    runner: CliRunner,
    video_scenes: Path,
    tmp_path: Path,
) -> None:
    """`scene --hflip` invierte horizontalmente."""
    output = tmp_path / "scene_hflip.jpg"

    result = runner.invoke(
        app,
        [
            "scene",
            str(video_scenes),
            "-o",
            str(output),
            "-ov",
            "yes",
            "--hflip",
        ],
    )

    assert result.exit_code == 0
    assert len(list(tmp_path.glob("scene_hflip_*.jpg"))) >= 1


def test_scene_success_with_vflip(
    runner: CliRunner,
    video_scenes: Path,
    tmp_path: Path,
) -> None:
    """`scene --vflip` invierte verticalmente."""
    output = tmp_path / "scene_vflip.jpg"

    result = runner.invoke(
        app,
        [
            "scene",
            str(video_scenes),
            "-o",
            str(output),
            "-ov",
            "yes",
            "--vflip",
        ],
    )

    assert result.exit_code == 0
    assert len(list(tmp_path.glob("scene_vflip_*.jpg"))) >= 1


def test_scene_error_overwrite_never(
    runner: CliRunner,
    video_scenes: Path,
    tmp_path: Path,
) -> None:
    """`scene -ov never` falla cuando el fichero ya existe."""
    output = tmp_path / "scene_never.jpg"
    output.write_bytes(b"existing")

    result = runner.invoke(
        app,
        ["scene", str(video_scenes), "-o", str(output), "-ov", "never"],
    )

    assert result.exit_code != 0


def test_scene_error_crop_bigger_than_video_dimensions(
    runner: CliRunner,
    video_scenes: Path,
    tmp_path: Path,
) -> None:
    """`scene --crop` rechaza área mayor que las dimensiones del vídeo."""
    output = tmp_path / "scene_crop.jpg"

    result = runner.invoke(
        app,
        [
            "scene",
            str(video_scenes),
            "-o",
            str(output),
            "-ov",
            "yes",
            "--crop",
            "160,90,10,10",
        ],
    )

    assert result.exit_code != 0
    assert "Invalid crop area" in result.output


def test_scene_error_oversize_without_upscale(
    runner: CliRunner,
    video_scenes: Path,
    tmp_path: Path,
) -> None:
    """`scene --size` mayor que el vídeo sin `--upscale` ignora el escalado."""
    output = tmp_path / "scene_oversize.jpg"

    result = runner.invoke(
        app,
        [
            "scene",
            str(video_scenes),
            "-o",
            str(output),
            "-ov",
            "yes",
            "--size",
            "320x180",
        ],
    )

    assert result.exit_code == 0
    assert "Ignored scale" in result.output


def test_scene_error_timestamp_bigger_than_video_duration(
    runner: CliRunner,
    video_scenes: Path,
    tmp_path: Path,
) -> None:
    """`scene --start` rechaza marca de tiempo mayor que la duración."""
    output = tmp_path / "scene_timestamp.jpg"

    result = runner.invoke(
        app,
        [
            "scene",
            str(video_scenes),
            "-o",
            str(output),
            "-ov",
            "yes",
            "--start",
            "00:00:04",
        ],
    )

    assert result.exit_code != 0
    assert "exceeds video duration" in result.output


# =============================================================================
#  main (global)
# =============================================================================


def test_main_version(runner: CliRunner) -> None:
    """`--version` muestra la versión de la aplicación."""
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert "Version" in result.output


def test_main_help(runner: CliRunner) -> None:
    """`--help` muestra la ayuda global."""
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "pyMedia" in result.output


# =============================================================================
#  end
# =============================================================================
