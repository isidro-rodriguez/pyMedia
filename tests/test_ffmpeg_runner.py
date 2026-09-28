"""Pruebas del módulo `commands/base/ffmpeg_runner.py`.

Cubre los helpers de preparación, staging, commit y el ciclo de vida del proceso.
"""

import io
import queue
import subprocess
import sys
from datetime import timedelta
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from pymedia.commands.base.ffmpeg_runner import (
    STDERR,
    STDOUT,
    FfmpegProcess,
    ProgressTracker,
    commit_outputs,
    prepare_command,
    run_ffmpeg,
    stage_outputs,
)
from pymedia.errors import (
    CommandError,
    InvalidParameterError,
    OperativeSystemError,
    UserError,
)

_MODULE = "pymedia.commands.base.ffmpeg_runner"
_WRITE = (
    "import pathlib, sys\n"
    "for name in sys.argv[1:]:\n"
    " pathlib.Path(name).write_text('new')\n"
)
_PROBE = (
    "import pathlib, sys\n"
    "target = pathlib.Path(sys.argv[1])\n"
    "pathlib.Path(sys.argv[2]).write_text(str(target))\n"
    "target.write_text('new')\n"
)


def _command(script: str, *args: Path) -> list[str]:
    """Comando que ejecuta `script` con el intérprete de los tests."""
    return [sys.executable, "-u", "-c", script, *map(str, args)]


# =============================================================================
#  prepare_command
# =============================================================================


def _cmd(args: list[str]) -> list[str]:
    """Normaliza a una lista con el binario y las args."""
    return ["ffmpeg", *args]


@pytest.mark.parametrize(
    ("overwrite", "expected_flag"),
    [
        (True, "-y"),
        (False, "-n"),
    ],
)
def test_prepare_command_inserts_policy_for_ffmpeg(
    overwrite: bool, expected_flag: str
) -> None:
    """El binario ffmpeg recibe `-nostdin` y la política de sobrescritura."""
    cmd = _cmd(["-i", "in.mkv", "out.mp4"])
    prepared = prepare_command(cmd=cmd, overwrite=overwrite)

    assert prepared == ["ffmpeg", "-nostdin", expected_flag, "-i", "in.mkv", "out.mp4"]


def test_prepare_command_drops_previous_policy_flags() -> None:
    """Los flags `-y`/`-n` previos no se duplican."""
    cmd = ["ffmpeg", "-y", "-n", "out.mp4"]
    prepared = prepare_command(cmd=cmd, overwrite=True)

    assert prepared == ["ffmpeg", "-nostdin", "-y", "out.mp4"]


def test_prepare_command_matches_binary_stem() -> None:
    """La detección ignora extensión y directorios."""
    for binary in ["ffmpeg", "ffmpeg.exe", "/usr/bin/ffmpeg"]:
        cmd = [binary, "out.mp4"]
        prepared = prepare_command(cmd=cmd, overwrite=True)
        assert prepared[:3] == [binary, "-nostdin", "-y"]


def test_prepare_command_ignores_other_binaries() -> None:
    """Un binario que no es ffmpeg se devuelve sin modificar."""
    cmd = ["python", "-c", "pass", "out.mp4"]
    assert prepare_command(cmd=cmd, overwrite=True) is cmd


# =============================================================================
#  stage_outputs
# =============================================================================


def test_stage_outputs_redirects_every_destination(tmp_path: Path) -> None:
    """La última salida y las extra pasan a apuntar al temporal."""
    staging = tmp_path / "staging"
    first, last = tmp_path / "a.mka", tmp_path / "b.mka"

    staged = stage_outputs(
        cmd=["ffmpeg", "-i", "in.mkv", str(first), str(last)],
        outputs=[str(first)],
        staging=staging,
    )

    assert staged == [
        "ffmpeg",
        "-i",
        "in.mkv",
        str(staging / "a.mka"),
        str(staging / "b.mka"),
    ]


def test_stage_outputs_always_redirects_the_last_argument(tmp_path: Path) -> None:
    """La salida principal se redirige aunque no esté en `outputs` (plantilla)."""
    staging = tmp_path / "staging"
    template = tmp_path / "frame_%03d.png"

    staged = stage_outputs(
        cmd=["ffmpeg", "-i", "in.mkv", str(template)], outputs=[], staging=staging
    )

    assert staged[-1] == str(staging / "frame_%03d.png")


def test_stage_outputs_keeps_the_binary_and_the_inputs(tmp_path: Path) -> None:
    """El binario y los ficheros de entrada nunca se redirigen."""
    staging = tmp_path / "staging"
    output = tmp_path / "out.mp4"

    staged = stage_outputs(
        cmd=["ffmpeg", "-i", "in.mkv", str(output)],
        outputs=[str(output)],
        staging=staging,
    )

    assert staged[0] == "ffmpeg"
    assert staged[2] == "in.mkv"


def test_stage_outputs_never_redirects_the_binary(tmp_path: Path) -> None:
    """Aunque coincida con una salida, el primer argumento queda intacto."""
    staging = tmp_path / "staging"
    output = tmp_path / "ffmpeg"

    staged = stage_outputs(
        cmd=["ffmpeg", "in.mkv", str(output)],
        outputs=[str(output)],
        staging=staging,
    )

    assert staged[0] == "ffmpeg"
    assert staged[-1] == str(staging / "ffmpeg")


def test_stage_outputs_rejects_duplicate_names(tmp_path: Path) -> None:
    """Dos salidas homónimas en directorios distintos se rechazan."""
    first = tmp_path / "a" / "out.mkv"
    second = tmp_path / "b" / "out.mkv"

    with pytest.raises(InvalidParameterError, match="same file name: out.mkv"):
        stage_outputs(
            cmd=["ffmpeg", "-i", "in.mkv", str(first), str(second)],
            outputs=[str(first)],
            staging=tmp_path / ".pymedia-test",
        )


def test_stage_outputs_returns_a_copy_of_the_command(tmp_path: Path) -> None:
    """El comando y las salidas originales no se mutan."""
    output = tmp_path / "out.mkv"
    cmd = ["ffmpeg", "-i", "in.mkv", str(output)]
    outputs = [str(output)]

    staged = stage_outputs(cmd=cmd, outputs=outputs, staging=tmp_path / "stage")

    assert cmd == ["ffmpeg", "-i", "in.mkv", str(output)]
    assert outputs == [str(output)]
    assert staged[-1] != str(output)


# =============================================================================
#  commit_outputs
# =============================================================================


def _staged(tmp_path: Path, *names: str) -> tuple[Path, Path]:
    """Crea un temporal con las salidas dadas y su directorio de destino."""
    staging = tmp_path / ".pymedia-test"
    staging.mkdir()
    for name in names:
        (staging / name).write_text("new")
    dest = tmp_path / "dest"
    dest.mkdir()
    return staging, dest


def test_commit_outputs_moves_and_replaces(tmp_path: Path) -> None:
    """Con sobrescritura permitida el destino se reemplaza."""
    staging, dest = _staged(tmp_path, "out.mkv")
    (dest / "out.mkv").write_text("old")

    commit_outputs(staging=staging, dest_dir=dest, overwrite=True)

    assert (dest / "out.mkv").read_text() == "new"
    assert list(staging.iterdir()) == []


def test_commit_outputs_refuses_existing_without_overwrite(tmp_path: Path) -> None:
    """Sin permiso, la comprobación aborta antes de mover nada."""
    staging, dest = _staged(tmp_path, "out.mkv", "free.mka")
    (dest / "out.mkv").write_text("old")

    with pytest.raises(CommandError, match="already exists"):
        commit_outputs(staging=staging, dest_dir=dest, overwrite=False)

    assert (dest / "out.mkv").read_text() == "old"
    assert sorted(p.name for p in staging.iterdir()) == ["free.mka", "out.mkv"]


def test_commit_outputs_reports_move_failure_as_os_error(tmp_path: Path) -> None:
    """Un `replace` fallido se informa como OperativeSystemError conservando causa."""
    staging, dest = _staged(tmp_path, "out.mkv")

    with (
        patch.object(Path, "replace", side_effect=PermissionError),
        pytest.raises(OperativeSystemError, match="could not be moved") as exc,
    ):
        commit_outputs(staging=staging, dest_dir=dest, overwrite=True)

    assert isinstance(exc.value.__cause__, PermissionError)


def test_commit_outputs_accepts_an_empty_staging(tmp_path: Path) -> None:
    """Un temporal sin salidas no falla."""
    staging = tmp_path / ".pymedia-test"
    staging.mkdir()

    commit_outputs(staging=staging, dest_dir=tmp_path, overwrite=True)

    assert list(tmp_path.iterdir()) == [staging]


# =============================================================================
#  ProgressTracker
# =============================================================================


def _make_tracker(progress_time=None, total_steps=None) -> ProgressTracker:
    return ProgressTracker(progress_time=progress_time, total_steps=total_steps)


def test_tracker_total_depends_on_settings() -> None:
    """El total viene del tiempo, de los pasos o de ninguno; manda el tiempo."""
    from datetime import timedelta

    assert _make_tracker(progress_time=timedelta(seconds=90)).total == 90.0
    assert _make_tracker(total_steps=4).total == 4.0
    assert _make_tracker(progress_time=None, total_steps=None).total is None
    assert (
        _make_tracker(progress_time=timedelta(seconds=30), total_steps=4).total == 30.0
    )


def test_tracker_updates_for_out_time() -> None:
    """`out_time_ms` se traduce a segundos."""
    tracker = _make_tracker(progress_time=timedelta(seconds=10))
    assert tracker.update(source=STDOUT, line="out_time_ms=1500000\n") == 1.5


def test_tracker_ignores_malformed_out_time() -> None:
    """Un valor no numérico no mueve la barra."""
    tracker = _make_tracker(progress_time=timedelta(seconds=10))
    assert tracker.update(source=STDOUT, line="out_time_ms=N/A\n") is None


def test_tracker_ignores_unrelated_lines() -> None:
    """Las líneas sin prefijo esperado no cuentan."""
    tracker = _make_tracker(progress_time=timedelta(seconds=10))
    assert tracker.update(source=STDOUT, line="frame=1\n") is None


def test_tracker_counts_showinfo_steps_from_stderr() -> None:
    """Cada `pts_time` de stderr avanza un paso; stdout no cuenta."""
    tracker = _make_tracker(total_steps=3)
    assert tracker.update(source=STDERR, line="pts_time:1\n") == 1.0
    assert tracker.update(source=STDERR, line="pts_time:2\n") == 2.0
    assert tracker.update(source=STDOUT, line="pts_time:3\n") is None


def test_tracker_without_settings_reports_nothing() -> None:
    """Sin parámetros no hay progreso que actualizar."""
    tracker = _make_tracker(progress_time=None, total_steps=None)

    assert tracker.update(source=STDOUT, line="out_time_ms=1000\n") is None
    assert tracker.update(source=STDERR, line="pts_time:1\n") is None


# =============================================================================
#  FfmpegProcess
# =============================================================================


def _popen(stdout: str = "", stderr: str = "") -> MagicMock:
    """Doble de `Popen` con pipes de texto en memoria."""
    proc = MagicMock(stdout=io.StringIO(stdout), stderr=io.StringIO(stderr))
    proc.wait.return_value = 0
    return proc


def test_process_starts_two_readers_and_returns_itself() -> None:
    """`__enter__` lanza el proceso con los streams y arranca dos lectores."""
    proc = _popen()
    with (
        patch(f"{_MODULE}.subprocess.Popen", return_value=proc) as popen,
        patch(f"{_MODULE}.threading.Thread") as thread,
    ):
        with FfmpegProcess(cmd=["ffmpeg", "out.mp4"], capture_steps=False) as running:
            assert running._proc is proc

    kwargs = popen.call_args.kwargs
    assert kwargs["args"] == ["ffmpeg", "out.mp4"]
    assert kwargs["stdout"] == subprocess.PIPE
    assert kwargs["stderr"] == subprocess.PIPE
    assert kwargs["stdin"] == subprocess.DEVNULL
    assert (kwargs["text"], kwargs["errors"], kwargs["bufsize"]) == (True, "replace", 1)
    assert thread.call_count == 2
    assert thread.return_value.start.call_count == 2


def test_exit_kills_a_live_process_and_closes_pipes() -> None:
    """Al salir se mata el proceso vivo, se espera a los lectores y se cierran."""
    proc = _popen()
    proc.poll.return_value = None
    threads = [MagicMock(), MagicMock()]
    with (
        patch(f"{_MODULE}.subprocess.Popen", return_value=proc),
        patch(f"{_MODULE}.threading.Thread", side_effect=threads),
    ):
        with FfmpegProcess(cmd=["ffmpeg"], capture_steps=False):
            pass

    proc.kill.assert_called_once()
    proc.wait.assert_called()
    assert all(t.join.called for t in threads)
    assert proc.stdout.closed and proc.stderr.closed


def test_exit_does_not_kill_a_finished_process() -> None:
    """Un proceso ya terminado no se mata."""
    proc = _popen()
    proc.poll.return_value = 0
    with (
        patch(f"{_MODULE}.subprocess.Popen", return_value=proc),
        patch(f"{_MODULE}.threading.Thread"),
    ):
        with FfmpegProcess(cmd=["ffmpeg"], capture_steps=False):
            pass

    proc.kill.assert_not_called()


def test_exit_closes_only_present_streams() -> None:
    """`__exit__` tolera un proceso sin alguno de los pipes."""
    proc = MagicMock(stdout=None, stderr=None)
    proc.poll.return_value = 0
    running = FfmpegProcess(cmd=["ffmpeg"], capture_steps=False)
    running._proc = proc

    running.__exit__()

    proc.kill.assert_not_called()
    proc.wait.assert_called_once()


def test_exit_without_entering_is_a_noop() -> None:
    """Sin `__enter__` no hay proceso que limpiar."""
    FfmpegProcess(cmd=["ffmpeg"], capture_steps=False).__exit__()


def test_pump_publishes_every_line_from_stdout() -> None:
    """Todas las líneas de stdout llegan a la cola, acabando en el sentinel."""
    running = FfmpegProcess(cmd=["ffmpeg"], capture_steps=False)

    running._pump(STDOUT, io.StringIO("a\nb\n"))

    assert [running._events.get_nowait() for _ in range(3)] == [
        (STDOUT, "a\n"),
        (STDOUT, "b\n"),
        (STDOUT, None),
    ]


def test_pump_stores_stderr_and_filters_showinfo() -> None:
    """Stderr se guarda entero; solo `pts_time` se emite si se piden pasos."""
    running = FfmpegProcess(cmd=["ffmpeg"], capture_steps=True)

    running._pump(STDERR, io.StringIO("frame=1\n[Parsed_showinfo_1] pts_time:2\n"))

    assert running.stderr_lines == [
        "frame=1\n",
        "[Parsed_showinfo_1] pts_time:2\n",
    ]
    assert [running._events.get_nowait() for _ in range(2)] == [
        (STDERR, "[Parsed_showinfo_1] pts_time:2\n"),
        (STDERR, None),
    ]


def test_events_stops_after_both_streams_finish() -> None:
    """El generador termina al recibir el sentinel de cada stream."""
    running = FfmpegProcess(cmd=["ffmpeg"], capture_steps=False)
    running._events.put((STDOUT, "a\n"))
    running._events.put((STDERR, None))
    running._events.put((STDOUT, None))

    assert list(running.events(stall_timeout=1)) == [(STDOUT, "a\n")]


def test_events_raises_when_nothing_arrives() -> None:
    """Sin eventos en el plazo, el error de cola se propaga al runner."""
    running = FfmpegProcess(cmd=["ffmpeg"], capture_steps=False)

    with pytest.raises(queue.Empty):
        list(running.events(stall_timeout=0.01))


def test_wait_returns_the_exit_code() -> None:
    """`wait` delega en el proceso."""
    running = FfmpegProcess(cmd=["ffmpeg"], capture_steps=False)
    running._proc = _popen()
    running._proc.wait.return_value = 3

    assert running.wait() == 3


def test_stderr_tail_keeps_the_last_ten_lines() -> None:
    """El diagnóstico final solo incluye las últimas líneas de stderr."""
    running = FfmpegProcess(cmd=["ffmpeg"], capture_steps=False)
    running.stderr_lines = [f"line {i}\n" for i in range(12)]

    assert running.stderr_tail == "".join(running.stderr_lines[-10:]).strip()


def test_stderr_tail_is_empty_without_output() -> None:
    """Sin stderr acumulado, el diagnóstico queda vacío."""
    assert FfmpegProcess(cmd=["ffmpeg"], capture_steps=False).stderr_tail == ""


# =============================================================================
#  run_ffmpeg integration
# =============================================================================


def _run(cmd: list[str], outputs: list[Path], **kwargs: Any) -> None:
    """Invoca el runner con los valores por defecto para testing."""
    run_ffmpeg(
        cmd=cmd,
        description="Test",
        outputs=outputs,
        overwrite=True,
        stall_timeout=5,
        command_name="Test",
        **kwargs,
    )


def test_run_ffmpeg_stages_and_prepares_the_command(tmp_path: Path) -> None:
    """El runner entrega a ffmpeg el comando normalizado y apuntando al temporal."""
    output = tmp_path / "out.mkv"
    running = MagicMock()
    running.__enter__.return_value = running
    running.events.return_value = iter(())
    running.wait.return_value = 0

    with (
        patch(f"{_MODULE}.FfmpegProcess", return_value=running) as process,
        patch(f"{_MODULE}.Progress"),
    ):
        _run(
            cmd=["ffmpeg", "-i", "in.mkv", str(output)], outputs=[output], total_steps=3
        )

    staged = process.call_args.kwargs["cmd"]
    assert staged[:3] == ["ffmpeg", "-nostdin", "-y"]
    assert staged[3:5] == ["-i", "in.mkv"]
    assert Path(staged[5]).name == "out.mkv"
    assert Path(staged[5]).parent.name.startswith(".pymedia-")
    assert process.call_args.kwargs["capture_steps"] is True


def test_staging_lives_next_to_the_destination(tmp_path: Path) -> None:
    """El temporal es contiguo al destino, con el prefijo `.pymedia-`."""
    output = tmp_path / "out.mp4"
    probe = tmp_path / "staged.txt"

    _run(cmd=_command(_PROBE, output, probe), outputs=[output])

    staged = Path(probe.read_text())
    assert staged.parent.parent == tmp_path
    assert staged.parent.name.startswith(".pymedia-")
    assert staged.name == output.name
    assert not list(tmp_path.glob(".pymedia-*"))


def test_staging_handles_spaces_and_unicode_paths(tmp_path: Path) -> None:
    """Rutas con espacios y acentos sobreviven al staging y al movimiento."""
    folder = tmp_path / "mi vídeo ñ"
    folder.mkdir()
    output = folder / "salida final.mkv"

    _run(cmd=_command(_WRITE, output), outputs=[output])

    assert output.read_text() == "new"
    assert not list(folder.glob(".pymedia-*"))


def test_relative_output_stages_in_current_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Una salida relativa usa el directorio actual como destino."""
    monkeypatch.chdir(tmp_path)

    _run(cmd=_command(_WRITE, Path("out.mp4")), outputs=[Path("out.mp4")])

    assert (tmp_path / "out.mp4").read_text() == "new"
    assert not list(tmp_path.glob(".pymedia-*"))


def test_missing_destination_directory_is_reported(tmp_path: Path) -> None:
    """Un destino sin directorio se informa antes de lanzar el proceso."""
    output = tmp_path / "missing" / "out.mp4"

    with pytest.raises(OperativeSystemError, match="Destination directory"):
        _run(cmd=_command(_WRITE, output), outputs=[output])

    assert not output.parent.exists()
    assert not list(tmp_path.glob(".pymedia-*"))


def test_run_ffmpeg_rejects_duplicate_names_without_writing(tmp_path: Path) -> None:
    """Dos salidas homónimas no llegan a ejecutar nada."""
    first = tmp_path / "a" / "out.mkv"
    second = tmp_path / "b" / "out.mkv"
    first.parent.mkdir()
    second.parent.mkdir()

    with pytest.raises(InvalidParameterError, match="same file name"):
        _run(cmd=_command(_WRITE, first, second), outputs=[first])

    assert not first.exists() and not second.exists()
    assert not list(tmp_path.rglob(".pymedia-*"))


def test_progress_by_time_updates_the_bar(tmp_path: Path) -> None:
    """`out_time_ms` en stdout escala la barra hasta el final."""
    output = tmp_path / "out.mp4"
    script = (
        "import time\n"
        "for value in (1000000, 2000000):\n"
        " print(f'out_time_ms={value}', flush=True)\n"
        " time.sleep(0.01)\n"
    )

    with patch(f"{_MODULE}.Progress") as progress:
        _run(
            cmd=_command(script, output),
            outputs=[output],
            progress_time=timedelta(seconds=2),
        )

    bar = progress.return_value.__enter__.return_value
    assert bar.add_task.call_args.kwargs["total"] == 2.0
    assert [call.kwargs["completed"] for call in bar.update.call_args_list] == [
        1.0,
        2.0,
        2.0,
    ]


def test_progress_by_steps_counts_showinfo(tmp_path: Path) -> None:
    """Cada línea `pts_time` de stderr avanza un paso."""
    output = tmp_path / "out.mkv"
    script = (
        "import sys\n"
        "for value in (1, 2):\n"
        " print(f'[Parsed_showinfo_1] n:{value} pts_time:{value}',"
        " file=sys.stderr, flush=True)\n"
    )

    with patch(f"{_MODULE}.Progress") as progress:
        _run(cmd=_command(script, output), outputs=[output], total_steps=2)

    bar = progress.return_value.__enter__.return_value
    assert bar.add_task.call_args.kwargs["total"] == 2.0
    assert [call.kwargs["completed"] for call in bar.update.call_args_list] == [
        1.0,
        2.0,
        2.0,
    ]


def test_progress_is_indeterminate_without_settings(tmp_path: Path) -> None:
    """Sin parámetros la barra no tiene total y no se actualiza."""
    output = tmp_path / "out.mkv"

    with patch(f"{_MODULE}.Progress") as progress:
        _run(cmd=_command(_WRITE, output), outputs=[output])

    bar = progress.return_value.__enter__.return_value
    assert bar.add_task.call_args.kwargs["total"] is None
    bar.update.assert_not_called()


def test_failure_keeps_the_output_and_reports_stderr(tmp_path: Path) -> None:
    """Un returncode distinto de cero no toca el destino e informa del stderr."""
    output = tmp_path / "out.mp4"
    output.write_text("original")
    script = "import sys\nprint('boom on stderr', file=sys.stderr)\nsys.exit(1)\n"

    with (
        patch(f"{_MODULE}.Progress"),
        pytest.raises(CommandError) as exc,
    ):
        _run(cmd=_command(script, output), outputs=[output])

    assert "failed during execution" in str(exc.value)
    assert "boom on stderr" in str(exc.value)
    assert output.read_text() == "original"
    assert not list(tmp_path.glob(".pymedia-*"))


def test_stall_timeout_kills_the_process_and_keeps_the_output(
    tmp_path: Path,
) -> None:
    """El bloqueo mata el proceso y conserva el fichero preexistente."""
    output = tmp_path / "out.mp4"
    output.write_text("original")
    proc = _popen()
    proc.poll.return_value = None

    with (
        patch(f"{_MODULE}.subprocess.Popen", return_value=proc),
        patch(f"{_MODULE}.threading.Thread"),
        patch(f"{_MODULE}.Progress"),
        pytest.raises(CommandError, match="timed out"),
    ):
        run_ffmpeg(
            cmd=["ffmpeg", "-i", "in.mkv", str(output)],
            description="Test",
            outputs=[output],
            overwrite=False,
            stall_timeout=0.01,
            command_name="Test",
        )

    proc.kill.assert_called_once()
    assert output.read_text() == "original"
    assert not list(tmp_path.glob(".pymedia-*"))


def test_manual_interrupt_is_reported_as_user_error(tmp_path: Path) -> None:
    """Un Ctrl+C se traduce a UserError y no mueve las salidas."""
    output = tmp_path / "out.mp4"
    output.write_text("original")
    running = MagicMock()
    running.__enter__.return_value = running
    running.events.side_effect = KeyboardInterrupt

    with (
        patch(f"{_MODULE}.FfmpegProcess", return_value=running),
        patch(f"{_MODULE}.Progress"),
        pytest.raises(UserError, match="interrupted manually"),
    ):
        run_ffmpeg(
            cmd=["ffmpeg", "-i", "in.mkv", str(output)],
            description="Test",
            outputs=[output],
            overwrite=True,
            stall_timeout=5,
            command_name="Cut",
        )

    assert output.read_text() == "original"
    assert not list(tmp_path.glob(".pymedia-*"))


def test_every_output_reaches_its_destination(tmp_path: Path) -> None:
    """En salida múltiple, todas las rutas terminan en su destino final."""
    first, last = tmp_path / "a_0.mka", tmp_path / "a_1.mka"

    _run(cmd=_command(_WRITE, first, last), outputs=[first])

    assert first.read_text() == "new" and last.read_text() == "new"
    assert not list(tmp_path.glob(".pymedia-*"))


@pytest.mark.parametrize("overwrite", [True, False])
def test_existing_output_is_replaced_only_when_allowed(
    tmp_path: Path, overwrite: bool
) -> None:
    """Sin permiso de sobrescritura no se pisa un destino ya existente."""
    output = tmp_path / "out.mp4"
    output.write_text("old")

    if overwrite:
        _run(cmd=_command(_WRITE, output), outputs=[output])
    else:
        with pytest.raises(CommandError, match="already exists"):
            run_ffmpeg(
                cmd=_command(_WRITE, output),
                description="Test",
                outputs=[output],
                overwrite=False,
                stall_timeout=5,
                command_name="Test",
            )

    assert output.read_text() == ("new" if overwrite else "old")
    assert not list(tmp_path.glob(".pymedia-*"))


def test_move_failure_is_reported_as_os_error(tmp_path: Path) -> None:
    """Un fallo al mover la salida se informa como OperativeSystemError."""
    output = tmp_path / "out.mp4"

    with (
        patch.object(Path, "replace", side_effect=PermissionError),
        pytest.raises(OperativeSystemError, match="could not be moved"),
    ):
        _run(cmd=_command(_WRITE, output), outputs=[output])

    assert not output.exists()
    assert not list(tmp_path.glob(".pymedia-*"))
