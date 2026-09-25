"""Instancia de Typer y sus comandos."""

import platform
from pathlib import Path

import typer
from rich import print
from rich.panel import Panel

from pymedia import version
from pymedia.data.containers import (
    AUDIO_CONTAINERS,
    SUBTITLES_CONTAINERS,
    VIDEO_CONTAINERS,
)
from pymedia.errors import InvalidContainerError, UserError
from pymedia.locales import translate as _
from pymedia.types import MediaType  # noqa

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
    """Muestra la versión de la aplicación.

    Args:
        value: Si se solicitó explícitamente la versión.

    Raises:
        typer.Exit: Siempre que `value` es verdadero, tras mostrar la versión.
    """
    if value:
        version_text = _("Version")
        platform_text = _("Platform")
        subtitle_text = _("Ffmpeg CLI handler")

        print(
            Panel.fit(
                renderable=(
                    f"[dim]{version_text}:[/]   [bold]{version}[/]\n"
                    f"[dim]Python:[/]    {platform.python_version()}\n"
                    f"[dim]{platform_text}:[/]  {platform.platform()}"
                ),
                title=" 🐍 [bold]pyMedia[/] 🎬 ",
                subtitle=f" {subtitle_text} ",
                border_style="cyan",
                padding=(1, 4),
            )
        )
        raise typer.Exit()


def validate_conflict_output_options(
    media_input_list: list[Path], output: Path | None, output_directory: Path | None
) -> None:
    """Comprueba que no se han aportado combinaciones de opciones de salida ambiguas.

    Args:
        media_input_list: Lista de rutas de los ficheros de vídeo a procesar.
        output: Ruta absoluta del fichero de salida procesado.
        output_directory: Directorio de salida para lotes de ficheros.

    Raises:
        ExclusiveOptionsError: Si se aportan `output` y `output_directory`
            a la vez.
        OptionError: Si se indica una salida única con varias entradas.
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


def validate_audio_path(path: Path) -> Path:
    """Valida que la ruta indicada sea un fichero de audio existente.

    Args:
        path: Ruta a validar.
        media_type: Tipo de fichero multimedia cargado.

    Returns:
        La propia ruta si es un fichero.

    Raises:
        UserError: Si la ruta no es un fichero.
        InvalidContainerError: Si no es un contenedor de audio válido.
    """
    if not path.is_file():
        raise UserError(_("%(path)s is not a file.") % {"path": path})
    if path.suffix not in AUDIO_CONTAINERS:
        raise InvalidContainerError(
            extension=path.suffix,
            media_type=MediaType.AUDIO,
            supported=AUDIO_CONTAINERS,
        )
    return path


def validate_media_path(path: Path) -> Path:
    """Valida que la ruta indicada sea un fichero de vídeo existente.

    Args:
        path: Ruta a validar.
        media_type: Tipo de fichero multimedia cargado.

    Returns:
        La propia ruta si es un fichero.

    Raises:
        UserError: Si la ruta no es un fichero.
        InvalidContainerError: Si no es un contenedor de vídeo válido.
    """
    if not path.is_file():
        raise UserError(_("%(path)s is not a file.") % {"path": path})
    if path.suffix not in VIDEO_CONTAINERS:
        raise InvalidContainerError(
            extension=path.suffix,
            media_type=MediaType.VIDEO,
            supported=VIDEO_CONTAINERS,
        )
    return path


def validate_subtitles_path(path: Path) -> Path:
    """Valida que la ruta indicada sea un fichero de subtítulos existente.

    Args:
        path: Ruta a validar.
        media_type: Tipo de fichero multimedia cargado.

    Returns:
        La propia ruta si es un fichero.

    Raises:
        UserError: Si la ruta no es un fichero.
        InvalidContainerError: Si no es un contenedor de subtítulos válido.
    """
    if not path.is_file():
        raise UserError(_("%(path)s is not a file.") % {"path": path})
    if path.suffix not in SUBTITLES_CONTAINERS:
        raise InvalidContainerError(
            extension=path.suffix,
            media_type=MediaType.SUBTITLES,
            supported=SUBTITLES_CONTAINERS,
        )
    return path


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
