"""Pruebas del ciclo de vida de los procesos de BaseService."""

import _thread
import io
import queue
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from pymedia.commands.base_service import BaseService
from pymedia.errors import CommandError, OsError, UserError
from pymedia.models.config import App, Config


class _TestService(BaseService[object]):
    """Tipo concreto para probar la ejecución sin cargar configuración de usuario."""


def test_manual_interrupt_stops_real_process(tmp_path: Path) -> None:
    """Ctrl+C detiene un hijo activo, cierra los pipes y elimina su salida."""
    output = tmp_path / "partial.mp4"
    pipeline = object.__new__(_TestService)
    pipeline.debug = False
    pipeline.command_name = "Test"
    pipeline.config = object.__new__(Config)
    object.__setattr__(pipeline.config, "app", App(language="en", stall_timeout=5))
    processes: list[subprocess.Popen[str]] = []
    popen = subprocess.Popen
    ready = threading.Event()
    done = threading.Event()

    def launch(*, args: list[str], **kwargs: Any) -> subprocess.Popen[str]:
        """Conserva el proceso real para verificar y limpiar sus recursos."""
        proc = popen(args, **kwargs)
        processes.append(proc)
        ready.set()
        return proc

    def interrupt() -> None:
        """Interrumpe el hilo principal una vez creada la salida parcial."""
        if not ready.wait(5):
            return
        for _ in range(100):
            if done.wait(0.05):
                return
            if output.exists():
                _thread.interrupt_main()
                return

    command = [
        sys.executable,
        "-u",
        "-c",
        "import pathlib, sys, time\n"
        "pathlib.Path(sys.argv[1]).write_text('partial')\n"
        "while True:\n"
        " print('out_time_ms=1', flush=True)\n"
        " time.sleep(0.05)\n",
        str(output),
    ]
    interrupter = threading.Thread(target=interrupt)
    interrupter.start()
    try:
        with patch("pymedia.commands.base_service.subprocess.Popen", launch):
            try:
                pipeline.run_ffmpeg(command, "Test", [output])
            except UserError as error:
                assert "interrupted manually" in str(error)
            else:
                raise AssertionError("KeyboardInterrupt was not handled")
        assert len(processes) == 1
        proc = processes[0]
        assert proc.poll() is not None
        assert proc.stdout is not None and proc.stdout.closed
        assert proc.stderr is not None and proc.stderr.closed
        assert not output.exists()
    finally:
        done.set()
        interrupter.join(timeout=5)
        for proc in processes:
            if proc.poll() is None:
                proc.kill()
            proc.wait(timeout=5)
            if proc.stdout is not None:
                proc.stdout.close()
            if proc.stderr is not None:
                proc.stderr.close()


@pytest.mark.parametrize("phase", ["queue", "first_start", "second_start", "wait"])
def test_interrupt_cleans_initialized_resources(tmp_path: Path, phase: str) -> None:
    """La interrupción limpia también un arranque parcial y la espera final."""
    pipeline = object.__new__(_TestService)
    pipeline.debug = False
    pipeline.command_name = "Test"
    pipeline.config = MagicMock()
    output = tmp_path / "partial.mp4"
    output.touch()
    proc = MagicMock(stdout=io.StringIO(), stderr=io.StringIO(), returncode=0)
    proc.poll.return_value = None
    readers = [MagicMock(ident=1), MagicMock(ident=2)]
    events = MagicMock()
    events.get.side_effect = [("stdout", None), ("stderr", None)]
    match phase:
        case "queue":
            events.get.side_effect = KeyboardInterrupt
        case "first_start" | "second_start":
            index = 0 if phase == "first_start" else 1
            readers[index].start.side_effect = KeyboardInterrupt
            for reader in readers[index:]:
                reader.ident = None
        case "wait":
            proc.wait.side_effect = [KeyboardInterrupt, 0]

    with (
        patch("pymedia.commands.base_service.subprocess.Popen", return_value=proc),
        patch("pymedia.commands.base_service.threading.Thread", side_effect=readers),
        patch("pymedia.commands.base_service.queue.Queue", return_value=events),
        patch("pymedia.commands.base_service.Progress"),
        pytest.raises(UserError, match="interrupted manually"),
    ):
        pipeline.run_ffmpeg(["ffmpeg"], "Test", [output])

    proc.kill.assert_called_once()
    assert proc.stdout.closed and proc.stderr.closed
    assert not output.exists()
    for reader in readers:
        if reader.ident is None:
            reader.join.assert_not_called()
        else:
            reader.join.assert_called()


@pytest.mark.parametrize("scenario", ["timeout", "ffmpeg", "success", "unlink"])
def test_abort_preserves_error_kind(tmp_path: Path, scenario: str) -> None:
    """Los fallos del proceso y del borrado no se convierten en aborto manual."""
    pipeline = object.__new__(_TestService)
    pipeline.debug = False
    pipeline.command_name = "Test"
    pipeline.config = MagicMock()
    output = tmp_path / "partial.mp4"
    output.touch()
    proc = MagicMock(stdout=io.StringIO(), stderr=io.StringIO(), returncode=0)
    proc.poll.return_value = None if scenario in ("timeout", "unlink") else 0
    if scenario == "ffmpeg":
        proc.returncode = 1
        proc.poll.return_value = 1
    events = MagicMock()
    events.get.side_effect = [("stdout", None), ("stderr", None)]
    if scenario in ("timeout", "unlink"):
        events.get.side_effect = queue.Empty
    with (
        patch("pymedia.commands.base_service.subprocess.Popen", return_value=proc),
        patch("pymedia.commands.base_service.threading.Thread"),
        patch("pymedia.commands.base_service.queue.Queue", return_value=events),
        patch("pymedia.commands.base_service.Progress"),
    ):
        if scenario == "success":
            pipeline.run_ffmpeg(["ffmpeg"], "Test", [output])
        elif scenario == "unlink":
            with (
                patch.object(Path, "unlink", side_effect=PermissionError),
                pytest.raises(OsError, match="could not be deleted"),
            ):
                pipeline.run_ffmpeg(["ffmpeg"], "Test", [output])
        else:
            message = "timed out" if scenario == "timeout" else "failed during"
            with pytest.raises(CommandError, match=message):
                pipeline.run_ffmpeg(["ffmpeg"], "Test", [output])
    assert output.exists() == (scenario in ("success", "unlink"))
    assert proc.stdout.closed and proc.stderr.closed
    if scenario in ("success", "ffmpeg"):
        proc.kill.assert_not_called()
