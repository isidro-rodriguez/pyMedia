"""Instancia de Typer y sus comandos."""

import platform
import shutil
import subprocess
from pathlib import Path

import typer
from rich import box
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pymedia import version
from pymedia.data.containers import (
    AUDIO_CONTAINERS,
    SUBTITLES_CONTAINERS,
    VIDEO_CONTAINERS,
)
from pymedia.errors import InvalidContainerError, UserError
from pymedia.locales import translate as _
from pymedia.types import MediaType
from pymedia.ui import console

# =============================================================================
#  Instancia base
# =============================================================================

base_cli = typer.Typer(
    name="pyMedia",
    rich_markup_mode="rich",
    no_args_is_help=True,
)


# =============================================================================
#  Callbacks y funciones auxiliares de CLI
# =============================================================================


def show_help(ctx: typer.Context, value: bool) -> None:
    """Muestra el texto de ayuda del comando en el idioma activo.

    Args:
        ctx: Contexto Typer del comando invocado.
        value: Si se solicitó explícitamente la ayuda.

    Raises:
        typer.Exit: Siempre que `value` es verdadero, tras mostrar la ayuda.
    """
    if value:
        typer.echo(ctx.get_help())
        raise typer.Exit()


def show_version(value: bool) -> None:
    """Muestra la versión de la aplicación, de Python, de ffmpeg y la plataforma.

    Args:
        value: Si se solicitó explícitamente la versión.

    Raises:
        typer.Exit: Siempre que `value` es verdadero, tras mostrar la versión.
    """
    if not value:
        return

    details = Table.grid(padding=(0, 2))
    details.add_column(style="muted", no_wrap=True)
    details.add_column()
    details.add_row("Python", platform.python_version())
    details.add_row("ffmpeg", _ffmpeg_version())
    details.add_row(_("Platform"), platform.platform())

    header = Text.assemble(
        ("▶ ", "primary"),
        ("pyMedia ", "heading"),
        (version, "highlight"),
        "\n",
        (_("Ffmpeg CLI handler"), "muted"),
    )
    console.print(
        Panel.fit(
            Group(header, Text(""), details),
            border_style="border",
            box=box.ROUNDED,
            padding=(1, 3),
        )
    )
    raise typer.Exit()


def _ffmpeg_version() -> Text:
    """Versión de ffmpeg instalada, o aviso si no está en el `PATH`."""
    binary = shutil.which("ffmpeg")
    if binary is None:
        return Text(_("not found"), style="error")
    try:
        result = subprocess.run(
            [binary, "-version"], capture_output=True, text=True, check=True
        )
    except (OSError, subprocess.CalledProcessError):
        return Text(_("not found"), style="error")
    # Primera línea: "ffmpeg version <versión> Copyright ..."
    words = result.stdout.split()
    return Text(words[2] if len(words) > 2 else "?")


def validate_conflict_output_options(
    media_input_list: list[Path], output: Path | None, output_directory: Path | None
) -> None:
    """Comprueba que no se han aportado combinaciones de opciones de salida ambiguas.

    Args:
        media_input_list: Lista de rutas de los ficheros de vídeo a procesar.
        output: Ruta absoluta del fichero de salida procesado.
        output_directory: Directorio de salida para lotes de ficheros.

    Raises:
        UserError: Si se aportan `output` y `output_directory`
            a la vez, o si se indica una salida única con varias entradas.
    """
    if output is not None and output_directory is not None:
        raise UserError(
            msg=_(
                "The following options are mutually exclusive: output, output_directory"
            )
        )
    if output is not None and len(media_input_list) > 1:
        raise UserError(
            msg=_(
                "It is not allowed to specify an output with multiple inputs, "
                "use output directory instead."
            )
        )


def _validate_path(
    path: Path, containers: tuple[str, ...], media_type: MediaType
) -> Path:
    """Valida que `path` sea un fichero con extensión de `containers`."""
    if not path.is_file():
        raise UserError(_("%(path)s is not a file.") % {"path": path})
    if path.suffix not in containers:
        raise InvalidContainerError(
            extension=path.suffix, media_type=media_type, supported=containers
        )
    return path


def validate_audio_path(path: Path) -> Path:
    """Valida que la ruta indicada sea un fichero de audio existente.

    Args:
        path: Ruta a validar.

    Returns:
        La propia ruta si es un fichero.

    Raises:
        UserError: Si la ruta no es un fichero.
        InvalidContainerError: Si no es un contenedor de audio válido.
    """
    return _validate_path(path, containers=AUDIO_CONTAINERS, media_type=MediaType.AUDIO)


def validate_media_path(path: Path) -> Path:
    """Valida que la ruta indicada sea un fichero de vídeo existente.

    Args:
        path: Ruta a validar.

    Returns:
        La propia ruta si es un fichero.

    Raises:
        UserError: Si la ruta no es un fichero.
        InvalidContainerError: Si no es un contenedor de vídeo válido.
    """
    return _validate_path(path, containers=VIDEO_CONTAINERS, media_type=MediaType.VIDEO)


def validate_subtitles_path(path: Path) -> Path:
    """Valida que la ruta indicada sea un fichero de subtítulos existente.

    Args:
        path: Ruta a validar.

    Returns:
        La propia ruta si es un fichero.

    Raises:
        UserError: Si la ruta no es un fichero.
        InvalidContainerError: Si no es un contenedor de subtítulos válido.
    """
    return _validate_path(
        path, containers=SUBTITLES_CONTAINERS, media_type=MediaType.SUBTITLES
    )


def validate_media_path_list(paths: list[Path]) -> list[Path]:
    """Valida que cada ruta del listado sea un fichero de vídeo existente.

    Args:
        paths: Rutas a validar.

    Returns:
        El propio listado de rutas si todos son ficheros de vídeo válidos.

    Raises:
        UserError: Si alguna ruta no es un fichero.
        InvalidContainerError: Si alguna ruta no es un contenedor de vídeo válido.
    """
    for p in paths:
        validate_media_path(path=p)
    return paths
