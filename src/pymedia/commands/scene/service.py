"""Comando ``scene``: service."""

import glob
import re
from collections.abc import Iterator
from pathlib import Path

import typer

from pymedia.commands.base_service import BaseService
from pymedia.commands.scene.cmd import SceneCmd
from pymedia.commands.scene.parameters import SceneParameters
from pymedia.errors import MissingParameterError
from pymedia.locales import _
from pymedia.types import OverwriteMode


class SceneService(BaseService[SceneParameters]):
    """Comando de CLI que captura miniaturas en los cambios de escena."""

    def start(self) -> None:
        """Construye y ejecuta el comando ffmpeg de capturas por escena.

        Raises:
            MissingParameterError: Si falta el medio, el umbral de escena o la
                ruta de imagen de salida.
            CommandGenerationError: Si el comando ffmpeg no se pudo generar.
        """
        if self.params.media is None:
            raise MissingParameterError(name="media")

        cmd = SceneCmd(params=self.params).create()

        output = self.params.image_output
        if output is None:
            raise MissingParameterError(name="image_output")
        template = output.with_stem(f"{output.stem}_%03d")

        if self.params.overwrite != OverwriteMode.YES and not self._confirm_overwrite(
            output_template=template
        ):
            return

        self.display_cmd(cmd=cmd)

        self.run_ffmpeg(
            cmd=cmd,
            progress_time=self.params.get_range_time(),
            description=_("Generating thumbnail"),
            output_list=self._expected_outputs(template=template),
        )

        if not any(self._expected_outputs(template=template)):
            self.logger.warning(
                _("No scene changes detected: no thumbnails generated.")
            )
            return

        self.logger.info(
            msg=_("Thumbnail(s) generated successfully: %(output)s"),
            output=str(template).replace("%03d", "*"),
        )

    def _confirm_overwrite(self, output_template: Path) -> bool:
        """Detecta si existen archivos con patrón 'filename_XXX.ext'."""
        stem = output_template.stem
        suffix = output_template.suffix
        match = re.match(r"^(.+)_%03d$", stem)
        if not match:
            # Si no hay patrón reconocible, se aborta para seguridad
            self.logger.warning(_("Cannot resolve scene output pattern from template."))
            return False
        base_stem = match.group(1)

        directory = output_template.parent
        pattern = re.compile(rf"^{re.escape(base_stem)}_(\d{{3}}){re.escape(suffix)}$")

        existing_files: list[Path] = []
        if directory.exists():
            for item in directory.iterdir():
                if item.is_file() and pattern.match(item.name):
                    existing_files.append(item)

        if existing_files:
            self.logger.warning(
                _("Found existing scene thumbnail files: %(files)s")
                % {"files": ", ".join(f.name for f in existing_files)}
            )
            if self.params.overwrite == OverwriteMode.NO or not typer.confirm(
                _("Overwrite?")
            ):
                self.logger.warning(
                    _("Process skipped since output files already exist.")
                )
                return False
            self.params.overwrite = OverwriteMode.YES
        return True

    def _expected_outputs(self, template: Path) -> Iterator[Path]:
        """Resuelve en caliente las miniaturas parciales del patrón de escena."""
        match = re.match(r"^(.+)_%03d$", template.stem)
        if match is None:
            self.logger.warning(_("Cannot resolve scene output pattern from template."))
            return
        # glob.escape evita que caracteres especiales del nombre actúen de patrón.
        pattern = f"{glob.escape(match.group(1))}_??*{template.suffix}"
        yield from sorted(template.parent.glob(pattern))
