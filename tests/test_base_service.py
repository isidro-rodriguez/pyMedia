"""Pruebas del ciclo de vida de los procesos de BaseService.

El servicio base de los comandos vive en `commands/base/service.py` y delega
la ejecución de `run_ffmpeg` en `commands/base/ffmpeg_runner.py`, cuyas
pruebas propias están en `test_ffmpeg_runner.py`.
"""

import _thread
import subprocess
import sys
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from pymedia.commands.base.service import BaseService
from pymedia.errors import CommandError, OsError, UserError
from pymedia.models.config import App, Config
from pymedia.types import OverwriteMode

_MODULE = "pymedia.commands.base.service"
_RUNNER = "pymedia.commands.base.ffmpeg_runner"


@dataclass
class _Params:
    """Parámetros requeridos por el bound `_OverwriteParams` para testing."""

    overwrite: OverwriteMode


class _TestService(BaseService[_Params]):
    """Servicio concreto para probar sin cargar la configuración del usuario."""

    logger: MagicMock


def _service(
    overwrite: OverwriteMode = OverwriteMode.ASK,
    *,
    debug: bool = False,
    show_cmd: bool = False,
) -> _TestService:
    """Construye un servicio sin tocar la configuración ni el logger globales."""
    service = object.__new__(_TestService)
    service.debug = debug
    service.show_cmd = show_cmd
    service.command_name = "Test"
    service.config = object.__new__(Config)
    object.__setattr__(
        service.config,
        "app",
        App(language="en", stall_timeout=5),
    )
    service.logger = MagicMock()
    service.params = _Params(overwrite=overwrite)
    return service


def _writer_command(*outputs: Path) -> list[str]:
    """Comando que simula a ffmpeg escribiendo `new` en cada ruta recibida."""
    script = (
        "import pathlib, sys\n"
        "for name in sys.argv[1:]:\n"
        " pathlib.Path(name).write_text('new')\n"
    )
    return [sys.executable, "-c", script, *map(str, outputs)]


def test_display_cmd_prints_and_exits_when_show_cmd_is_true() -> None:
    """Cuando `show_cmd=True`, el comando se muestra y el proceso termina."""
    service = _service(show_cmd=True)
    cmd = ["ffmpeg", "-i", "in.mkv", "out.mp4"]

    with pytest.raises(SystemExit) as exc_info:
        service.display_cmd(cmd)
    assert exc_info.value.code == 0
    service.logger.print.assert_called_once()


def test_display_cmd_quotes_tokens_for_windows(tmp_path: Path) -> None:
    """En Windows, los tokens con caracteres especiales se entrecomillan."""
    service = _service(show_cmd=True)
    token = tmp_path / "my videos" / "a.mkv"

    with pytest.raises(SystemExit):
        service.display_cmd(["ffmpeg", "-i", str(token), "out.mp4"])

    rendered = service.logger.print.call_args.kwargs["renderable"]
    # En Windows espera '"my videos\a.mkv"'
    assert '"' in rendered and str(token) in rendered or rendered.count('"') == 2


def test_display_cmd_logs_command_in_default_mode() -> None:
    """Sin `show_cmd`, solo se registra el comando como DEBUG."""
    service = _service()
    cmd = ["ffmpeg", "-i", "in.mkv", "out.mp4"]
    service.display_cmd(cmd)

    assert service.logger.debug.call_args.kwargs["cmd"] == cmd


def test_display_cmd_aborts_process_when_debug_declined() -> None:
    """Si debug=True y se rechaza la confirmación, se aborta el comando."""
    service = _service(debug=True)

    with (
        patch(f"{_MODULE}.typer.confirm", return_value=False) as confirm,
        pytest.raises(SystemExit) as exc_info,
    ):
        service.display_cmd(["ffmpeg", "-i", "in.mkv", "out.mp4"])

    confirm.assert_called_once()
    assert exc_info.value.code == 0
    service.logger.warning.assert_called_once()
    service.logger.print.assert_not_called()


def test_resolve_overwrite_allows_when_policy_is_yes() -> None:
    """Con `overwrite=OverwriteMode.YES`, todo es permitido."""
    service = _service(overwrite=OverwriteMode.YES)

    assert service.resolve_overwrite([Path("x.mp4")])
    assert service.logger.warning.call_count == 0


def test_resolve_overwrite_rejects_existing_without_permission(tmp_path: Path) -> None:
    """Con `overwrite=OverwriteMode.NO`, se rechazan los ya existentes."""
    existing = tmp_path / "out.mp4"
    existing.write_text("old")

    service = _service(overwrite=OverwriteMode.NO)
    assert service.resolve_overwrite([existing]) is False
    service.logger.warning.assert_called_once()
    existing.unlink(missing_ok=True)


def test_resolve_overwrite_prompts_user_when_needed(tmp_path: Path) -> None:
    """Con `overwrite=OverwriteMode.ASK` se pregunta si el fichero existe."""
    service = _service(overwrite=OverwriteMode.ASK)
    output = tmp_path / "out.mp4"
    output.write_text("old")

    with patch(f"{_MODULE}.typer.confirm", return_value=True) as confirm:
        assert service.resolve_overwrite([output]) is True

    confirm.assert_called_once()
    assert service.params.overwrite == OverwriteMode.YES


def test_resolve_overwrite_aborts_when_user_declines(tmp_path: Path) -> None:
    """Si el usuario rechaza el prompt, el proceso se omite."""
    service = _service(overwrite=OverwriteMode.ASK)
    output = tmp_path / "out.mp4"
    output.write_text("old")

    with patch(f"{_MODULE}.typer.confirm", return_value=False):
        assert service.resolve_overwrite([output]) is False

    assert service.params.overwrite == OverwriteMode.ASK
    service.logger.warning.assert_called()


def test_success_moves_every_output_and_removes_temp(tmp_path: Path) -> None:
    """Con salida múltiple, todas las rutas llegan a su destino final."""
    first, last = tmp_path / "a_0.mka", tmp_path / "a_1.mka"
    pipeline = _service(OverwriteMode.YES)

    pipeline.run_ffmpeg(_writer_command(first, last), "Test", [first])

    assert first.read_text() == "new" and last.read_text() == "new"
    assert not list(tmp_path.glob(".pymedia-*"))


@pytest.mark.parametrize("overwrite", [OverwriteMode.YES, OverwriteMode.NO])
def test_existing_output_is_replaced_only_when_allowed(
    tmp_path: Path, overwrite: OverwriteMode
) -> None:
    """Sin permiso de sobrescritura no se pisa un destino ya existente."""
    output = tmp_path / "out.mp4"
    output.write_text("old")
    pipeline = _service(overwrite)

    if overwrite == OverwriteMode.YES:
        pipeline.run_ffmpeg(_writer_command(output), "Test", [output])
    else:
        with pytest.raises(CommandError, match="already exists"):
            pipeline.run_ffmpeg(_writer_command(output), "Test", [output])

    assert output.read_text() == ("new" if overwrite == OverwriteMode.YES else "old")
    assert not list(tmp_path.glob(".pymedia-*"))


def test_move_failure_is_reported_as_os_error(tmp_path: Path) -> None:
    """Un fallo al mover la salida se informa como OsError."""
    output = tmp_path / "out.mp4"
    pipeline = _service(OverwriteMode.YES)

    with (
        patch.object(Path, "replace", side_effect=PermissionError),
        pytest.raises(OsError, match="could not be moved"),
    ):
        pipeline.run_ffmpeg(_writer_command(output), "Test", [output])

    assert not output.exists()
    assert not list(tmp_path.glob(".pymedia-*"))


def test_manual_interrupt_stops_real_process(tmp_path: Path) -> None:
    """Ctrl+C detiene un hijo activo, descarta el temporal y respeta el original."""
    output = tmp_path / "partial.mp4"
    output.write_text("original")
    pipeline = object.__new__(_TestService)
    pipeline.debug = False
    pipeline.command_name = "Test"
    pipeline.config = object.__new__(Config)
    object.__setattr__(pipeline.config, "app", App(language="en", stall_timeout=5))
    pipeline.logger = MagicMock()
    pipeline.params = _Params(OverwriteMode.YES)

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
            if any(tmp_path.glob(".pymedia-*/partial.mp4")):
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
        with patch(f"{_RUNNER}.subprocess.Popen", launch):
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
        assert output.read_text() == "original"
        assert not list(tmp_path.glob(".pymedia-*"))
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
