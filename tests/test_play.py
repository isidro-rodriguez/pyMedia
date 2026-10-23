"""Tests del comando ``play``: composición de ffplay, validación y ejecución.

La reproducción abre una ventana, así que los tests de CLI usan `--show-cmd` y
los del servicio sustituyen `subprocess.run`.
"""

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
import typer
from helpers import Invoke

from pymedia.commands.play.parameters import PlayParameters
from pymedia.commands.play.service import PlayService
from pymedia.errors import CommandError, UserError
from pymedia.logger import Logger


@pytest.fixture
def subs_file(tmp_path: Path) -> Path:
    """Fichero SRT externo con nombre que exige escapado en el filtro."""
    path = tmp_path / "subs, eng.srt"
    path.write_text("1\n00:00:00,000 --> 00:00:01,000\nHello\n", encoding="utf-8")
    return path


# =============================================================================
#  Composición del comando (CLI con --show-cmd)
# =============================================================================


def test_play_minimal_command(pymedia: Invoke, video_mp4_a: Path) -> None:
    """Sin opciones, solo se pasa el fichero a ffplay."""
    result = pymedia("play", str(video_mp4_a), "--show-cmd")

    assert result.exit_code == 0, result.output
    # En Windows la ruta se muestra entre comillas (contiene `\\`).
    binary, path = result.output.strip().split(" ", 1)
    assert binary == "ffplay"
    assert path.strip("'\"") == str(video_mp4_a)


def test_play_range_and_playback_options(
    pymedia: Invoke, video_mkv_two_audio: Path
) -> None:
    """El final se convierte en duración y las opciones se traducen a ffplay."""
    result = pymedia(
        "play",
        str(video_mkv_two_audio),
        "--start",
        "00:00:01",
        "--end",
        "00:00:02",
        "--audio",
        "1",
        "--volume",
        "40",
        "--loop",
        "--fullscreen",
        "--show-cmd",
    )

    assert result.exit_code == 0, result.output
    assert "-ss 0:00:01 -t 0:00:01 -ast a:1 -volume 40 -loop 0 -fs" in result.output


def test_play_subtitles_track(pymedia: Invoke, video_mkv_subs: Path) -> None:
    """`--subs` selecciona la pista de subtítulos por índice de tipo."""
    result = pymedia("play", str(video_mkv_subs), "--subs", "1", "--show-cmd")

    assert result.exit_code == 0, result.output
    assert "-sst s:1" in result.output


@pytest.mark.parametrize(("option", "flag"), [("--mute", "-an"), ("--no-subs", "-sn")])
def test_play_disable_streams(
    pymedia: Invoke, video_mkv_subs: Path, option: str, flag: str
) -> None:
    """`--mute` y `--no-subs` desactivan el audio y los subtítulos."""
    result = pymedia("play", str(video_mkv_subs), option, "--show-cmd")

    assert result.exit_code == 0, result.output
    assert f" {flag} " in result.output


def test_play_filters_and_burned_subtitles(
    pymedia: Invoke, video_mp4_a: Path, subs_file: Path
) -> None:
    """Los subtítulos externos van antes que los filtros y ocultan los internos."""
    result = pymedia(
        "play",
        str(video_mp4_a),
        "--burn-subtitles",
        str(subs_file),
        "--hflip",
        "--show-cmd",
    )

    assert result.exit_code == 0, result.output
    assert "-vf" in result.output
    assert "subtitles=" in result.output
    assert ",hflip" in result.output
    assert " -sn " in result.output


# =============================================================================
#  Validación de opciones
# =============================================================================


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (("--mute", "--audio", "0"), "cannot be combined: --mute, --audio"),
        (("--subs", "0", "--no-subs"), "cannot be combined: --subs, --no-subs"),
        (("--volume", "101"), "Volume must be between 0 and 100."),
        (("--volume", "-1"), "Volume must be between 0 and 100."),
        (("--audio", "5"), "Audio index not included."),
        (("--subs", "0"), "Subtitles index not included."),
        (("--start", "00:00:01", "--end", "00:00:00"), "Invalid timestamps"),
    ],
)
def test_play_rejects_invalid_options(
    pymedia: Invoke, video_mp4_a: Path, args: tuple[str, ...], message: str
) -> None:
    """Las combinaciones excluyentes y los valores fuera de rango se rechazan."""
    result = pymedia("play", str(video_mp4_a), *args, "--show-cmd")

    assert result.exit_code != 0
    assert message in result.output


def test_play_burned_subtitles_exclusive_with_subs(
    pymedia: Invoke, video_mkv_subs: Path, subs_file: Path
) -> None:
    """No se puede dibujar un fichero externo y elegir una pista interna a la vez."""
    result = pymedia(
        "play",
        str(video_mkv_subs),
        "--subs",
        "0",
        "--burn-subtitles",
        str(subs_file),
        "--show-cmd",
    )

    assert result.exit_code != 0
    assert "cannot be combined: --subs, --burn-subtitles" in result.output


# =============================================================================
#  Servicio
# =============================================================================


@pytest.fixture
def service(video_mp4_a: Path) -> PlayService:
    """Servicio de `play` con parámetros mínimos sobre un vídeo real."""
    Logger.create()
    return PlayService(params=PlayParameters.load(media_input=video_mp4_a))


def test_play_service_runs_ffplay(service: PlayService) -> None:
    """Ejecuta ffplay con el comando compuesto y sin capturar su salida."""
    completed = subprocess.CompletedProcess(args=[], returncode=0)
    with (
        patch("shutil.which", return_value="/usr/bin/ffplay"),
        patch("subprocess.run", return_value=completed) as run,
    ):
        service.start()

    cmd = run.call_args.args[0]
    assert cmd[0] == "/usr/bin/ffplay"
    assert service.params.media is not None
    assert cmd[-1] == str(service.params.media.path)


def test_play_service_requires_ffplay(service: PlayService) -> None:
    """Sin ffplay en el `PATH` se informa al usuario y no se ejecuta nada."""
    with (
        patch("shutil.which", return_value=None),
        patch("subprocess.run") as run,
        pytest.raises(UserError, match="ffplay was not found in PATH"),
    ):
        service.start()

    run.assert_not_called()


def test_play_service_reports_ffplay_error(service: PlayService) -> None:
    """Un código de salida distinto de cero se convierte en `CommandError`."""
    completed = subprocess.CompletedProcess(args=[], returncode=1)
    with (
        patch("shutil.which", return_value="/usr/bin/ffplay"),
        patch("subprocess.run", return_value=completed),
        pytest.raises(CommandError, match="exit code 1"),
    ):
        service.start()


def test_play_service_ignores_ctrl_c(service: PlayService) -> None:
    """Ctrl+C cierra la reproducción sin mostrar un error."""
    with (
        patch("shutil.which", return_value="/usr/bin/ffplay"),
        patch("subprocess.run", side_effect=KeyboardInterrupt),
    ):
        service.start()


def test_play_service_show_cmd_does_not_need_ffplay(video_mp4_a: Path) -> None:
    """`--show-cmd` muestra el comando aunque ffplay no esté instalado."""
    Logger.create()
    service = PlayService(
        params=PlayParameters.load(media_input=video_mp4_a), show_cmd=True
    )
    with patch("shutil.which", return_value=None), pytest.raises(typer.Exit):
        service.start()
