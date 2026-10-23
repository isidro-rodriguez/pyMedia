"""Comando ``scene``: service."""

import re
from collections.abc import Iterator
from pathlib import Path

from pymedia.commands.base.service import BaseService
from pymedia.commands.scene.cmd import SceneCmd
from pymedia.commands.scene.parameters import SceneParameters
from pymedia.errors import MissingParameterError
from pymedia.locales import translate as _
from pymedia.types import OverwriteMode
from pymedia.ui import confirm


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

        self.logger.success(
            msg=_("Thumbnail(s) generated successfully: %(output)s"),
            output=str(template).replace("%03d", "*"),
        )

    def _confirm_overwrite(self, output_template: Path) -> bool:
        """Detecta si existen archivos con patrón 'filename_XXX.ext'."""
        if self.show_cmd:
            return True
        stem = output_template.stem
        suffix = output_template.suffix
        match = re.match(r"^(.+)_%03d$", stem)
        if not match:
            # Si no hay patrón reconocible, se aborta para seguridad
            self.logger.warning(_("Cannot resolve scene output pattern from template."))
            return False
        base_stem = match.group(1)

        directory = output_template.parent
        pattern = _numbered_pattern(base_stem=base_stem, suffix=suffix)

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
            if self.params.overwrite == OverwriteMode.NO or not confirm(
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
        if not template.parent.is_dir():
            return
        pattern = _numbered_pattern(base_stem=match.group(1), suffix=template.suffix)
        yield from sorted(
            path for path in template.parent.iterdir() if pattern.match(path.name)
        )


def _numbered_pattern(base_stem: str, suffix: str) -> re.Pattern[str]:
    """Patrón de las miniaturas `base_NNN.ext` que genera la plantilla `%03d`.

    `%03d` rellena hasta 3 cifras pero no limita: la miniatura 1000 se llama
    `base_1000.ext`. Se excluyen nombres ajenos como `base_backup.ext`.
    """
    return re.compile(rf"^{re.escape(base_stem)}_\d{{3,}}{re.escape(suffix)}$")
