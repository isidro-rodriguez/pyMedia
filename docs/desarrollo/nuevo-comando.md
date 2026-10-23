# Añadir un comando

Esta receta crea un comando de ejemplo, `clean`, que elimina metadatos y capítulos de un
vídeo sin recodificar. Sirve de plantilla para cualquier comando nuevo; copia un comando
existente parecido cuando sea posible.

## 1. Estructura

```text
src/pymedia/commands/clean/
├── __init__.py
├── cli.py
├── parameters.py
├── cmd.py
└── service.py
```

`__init__.py` solo lleva un docstring breve:

```python
"""Comando ``clean``: elimina metadatos y capítulos de un contenedor."""
```

## 2. Parámetros

Reutiliza mixins antes de escribir lógica nueva. Si una validación puede servir a otros
comandos, crea un mixin en `src/pymedia/mixins/`.

```python
"""Comando ``clean``: procesador de parámetros."""

from dataclasses import dataclass
from pathlib import Path
from typing import Self

from pymedia.commands.base.parameters import BaseParameters
from pymedia.mixins.media_mixin import MediaInputMixin
from pymedia.mixins.outputs_mixin import MediaOutputMixin
from pymedia.types import OverwriteMode


@dataclass(kw_only=True)
class CleanParameters(BaseParameters, MediaInputMixin, MediaOutputMixin):
    """Parámetros utilizados por el comando Clean."""

    @classmethod
    def load(
        cls,
        overwrite: OverwriteMode,
        media_input: Path,
        media_output: Path | None = None,
    ) -> Self:
        """Valida y parsea los argumentos en parámetros procesados.

        Args:
            overwrite: Política de conflicto ante fichero de salida existente.
            media_input: Ruta del fichero de vídeo a procesar.
            media_output: Ruta del fichero de salida.

        Returns:
            Parámetros procesados y validados para el comando clean.
        """
        params = cls(overwrite=overwrite)
        params.create_media_input(media_input=media_input, logger=params.logger)
        params.create_media_output(
            extension=media_input.suffix,
            affix="_clean",
            output=media_output,
            remux=True,
        )
        return params
```

## 3. Comando ffmpeg

`cmd.py` es una función pura: no escribe logs ni accede a disco. No añadas `-y`, `-n`,
`-progress` ni `-nostats`: los gestiona `ffmpeg_runner.prepare_command`.

```python
"""Comando ``clean``: compositor del comando ffmpeg."""

from pymedia.commands.clean.parameters import CleanParameters
from pymedia.errors import MissingParameterError


class CleanCmd:
    """Compone el comando ffmpeg que limpia los metadatos de un contenedor."""

    def __init__(self, params: CleanParameters) -> None:
        """Inicializa el compositor con los parámetros validados."""
        self.params = params

    def create(self) -> list[str]:
        """Crea el comando de ffmpeg.

        Returns:
            Lista de cadenas de texto con el comando ffmpeg.

        Raises:
            MissingParameterError: Si falta el medio o la salida.
        """
        if self.params.media is None:
            raise MissingParameterError(name="media")
        if self.params.media_output is None:
            raise MissingParameterError(name="media_output")

        return [
            "ffmpeg",
            "-i",
            str(self.params.media.path),
            "-map",
            "0",
            "-c",
            "copy",
            "-map_metadata",
            "-1",
            "-map_chapters",
            "-1",
            str(self.params.media_output),
        ]
```

## 4. Servicio

```python
"""Comando ``clean``: service."""

from pymedia.commands.base.service import BaseService
from pymedia.commands.clean.cmd import CleanCmd
from pymedia.commands.clean.parameters import CleanParameters
from pymedia.errors import MissingParameterError
from pymedia.locales import translate as _


class CleanService(BaseService[CleanParameters]):
    """Comando de CLI que elimina metadatos y capítulos de un contenedor."""

    def start(self) -> None:
        """Construye el comando ffmpeg y ejecuta la limpieza.

        Raises:
            MissingParameterError: Si falta la salida procesada.
        """
        output = self.params.media_output
        if output is None:
            raise MissingParameterError(name="media_output")
        if not self.resolve_overwrite(output_list=[output]):
            return

        cmd = CleanCmd(params=self.params).create()
        self.display_cmd(cmd=cmd)
        self.run_ffmpeg(
            cmd=cmd,
            description=_("Cleaning metadata"),
            output_list=[output],
            progress_time=self.params.media.duration if self.params.media else None,
        )
        self.logger.info(
            msg=_("Metadata cleaned successfully: %(output)s"), output=output
        )
```

- `progress_time` activa la barra por tiempo; `total_steps` la activa por pasos.
- `output_list` debe contener **todas** las salidas que genera ffmpeg: el runner las
  redirige al temporal y las confirma al final.

## 5. CLI

Usa los tipos de `commands/base/cli_options.py` para que las opciones sean idénticas en
todos los comandos. El texto de ayuda se escribe en inglés y se traduce con `_()`.

```python
"""Comando ``clean``: cli."""

import typer

from pymedia.commands.base.cli_options import (
    DebugOption,
    HelpOption,
    MediaInputArgument,
    OutputOption,
    OverwriteOption,
    ShowCmdOption,
)
from pymedia.commands.clean.parameters import CleanParameters
from pymedia.commands.clean.service import CleanService
from pymedia.locales import translate as _
from pymedia.logger import Logger
from pymedia.types import OverwriteMode

clean_cli = typer.Typer()

CLEAN_HELP = _(
    """\
Remove metadata and chapters from a media file without transcoding.

[bold]Examples[/bold]:
  Remove all metadata:
    > pymedia clean input.mp4
"""
)


@clean_cli.command(
    name="clean",
    help=CLEAN_HELP,
    rich_help_panel=_("Video commands"),
    no_args_is_help=True,
)
def clean(
    media_input: MediaInputArgument,
    media_output: OutputOption = None,
    overwrite: OverwriteOption = OverwriteMode.ASK,
    debug: DebugOption = False,
    show_cmd: ShowCmdOption = False,
    _help: HelpOption = False,
) -> None:
    """Punto de entrada del comando ``clean``.

    Args:
        media_input: Ruta del fichero de vídeo a procesar.
        media_output: Ruta del fichero de salida.
        overwrite: Política ante conflicto de salida ya existente.
        debug: Habilita el nivel de log DEBUG.
        show_cmd: Muestra el comando ffmpeg compuesto sin ejecutarlo.
        _help: Helper para mostrar esta línea en distintos idiomas.
    """
    Logger.create(debug=debug)
    params = CleanParameters.load(
        overwrite=overwrite, media_input=media_input, media_output=media_output
    )
    CleanService(debug=debug, show_cmd=show_cmd, params=params).start()
```

## 6. Registro en la aplicación

En `src/pymedia/main.py`, dentro de `_build_app()`:

```python
from pymedia.commands.clean.cli import clean_cli

...
built_app.add_typer(clean_cli)
```

El import va dentro de la función para que el idioma esté fijado antes de evaluar los
textos de ayuda. El orden de `add_typer` es el orden en la ayuda.

## 7. Tests

| Test                         | Dónde                         | Qué comprobar                                              |
|------------------------------|-------------------------------|------------------------------------------------------------|
| Composición del comando      | `tests/test_<comando>_cmd.py` | La lista que devuelve `create()` para casos representativos. |
| Validaciones de mixins nuevos| `tests/test_mixins_*.py`      | Entradas válidas, límites y mensajes de error.             |
| Extremo a extremo            | `tests/test_cli.py`           | Con la fixture `pymedia`: código de salida, mensajes y salida con `stream_types()`. |

Ejemplo extremo a extremo (se ejecuta como CLI en proceso y, con la marca `binary`,
contra el ejecutable compilado):

```python
def test_clean_success_removes_metadata(
    pymedia: Invoke, video_mp4_a: Path, tmp_path: Path
) -> None:
    """`clean` copia las pistas y elimina los metadatos globales."""
    output = tmp_path / "clean.mp4"

    result = pymedia("clean", str(video_mp4_a), "-o", str(output), "-ov", "yes")

    assert result.exit_code == 0
    assert stream_types(output) == ["video", "audio"]
```

## 8. Traducciones y documentación

1. Ejecuta el flujo de [traducciones](contribuir.md#traducciones) y traduce los
   `msgid` nuevos en `spanish/LC_MESSAGES/pymedia.po`.
2. Documenta el comando en `docs/usuario/comandos/` y añádelo a la tabla del
   `README.md`.
3. Añade la entrada en `CHANGELOG.md` bajo `[Sin publicar]` → `Añadido`.
4. Pasa la [definición de terminado](contribuir.md#definición-de-terminado).
