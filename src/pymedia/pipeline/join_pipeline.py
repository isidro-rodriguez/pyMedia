"""Subcomando `join`: une múltiples contenedores en uno solo."""

import tempfile
from pathlib import Path

from pymedia.errors import (
    IncompatibleMediaError,
    MissingParameterError,
)
from pymedia.ffmpeg.join_cmd import JoinCmd
from pymedia.locales import _  # noqa
from pymedia.models.parameters import JoinParameters
from pymedia.pipeline.base_pipeline import BasePipeline
from pymedia.types import OverwriteMode


class JoinPipeline(BasePipeline[JoinParameters]):
    """Comando de CLI para la unión de múltiples contenedores."""

    def process_parameters(
        self,
        media_input_list: list[Path],
        overwrite: OverwriteMode,
        media_output: Path | None = None,
    ) -> None:
        """Valida y parsea los argumentos en parámetros procesados."""
        params = JoinParameters(
            overwrite=overwrite,
        )

        params.create_media_list(
            media_input_list=media_input_list,
            logger=self.logger,
        )

        params.create_media_output(
            extension=self.config.default_containers.media,
            output=media_output,
            media_list=params.media_list,
            remux=True,
        )

        self.params = params

    def process_cmd(self) -> None:
        """Construye el comando ffmpeg y ejecuta la unión de los ficheros multimedia."""
        if self.params.media_list is None:
            raise MissingParameterError(name="media_list")
        if self.params.media_output is None:
            raise MissingParameterError(name="media_output")

        if not self.resolve_overwrite(output_list=[self.params.media_output]):
            return

        self._check_media_compatibility()

        with tempfile.TemporaryDirectory() as tmp_dir:
            list_txt = Path(tmp_dir) / "list.txt"

            with list_txt.open(mode="w", encoding="utf-8", newline="\n") as file:
                for media in self.params.media_list:
                    raw_path = str(media.path)
                    # Resolución de quoting potencialmente problemático.
                    if "'" in raw_path:
                        escaped_path = f'"{raw_path}"'
                    else:
                        escaped_path = f"'{raw_path}'"
                    file.write(f"file {escaped_path}\n")

            cmd = JoinCmd(params=self.params).create(list_txt=list_txt)

            self.logger.debug(_("FFmpeg command: %(cmd)s"), cmd=cmd)

            self.run_ffmpeg(
                cmd=cmd,
                description=_("Joining media files"),
            )

        self.logger.info(
            msg=_("Containers joined successfully: %(output)s"),
            output=self.params.media_output,
        )

    def _check_media_compatibility(self) -> None:
        """Comprueba que todos los medios de la lista son compatibles con el primero.

        Raises:
            IncompatibleMediaError: Si alguno de los medios tiene propiedades
                incompatibles con el primer medio de la lista.
        """
        if self.params.media_output is None:
            raise MissingParameterError(name="media_output")
        if self.params.media_list is None or len(self.params.media_list) < 2:
            return

        first = self.params.media_list[0]
        incompatible: list[tuple[Path, list[str]]] = []

        def _prop(label: str, first_value: object, value: object) -> str | None:
            if first_value != value:
                return f"{label} differs: {first_value} vs {value}"
            return None

        for media in self.params.media_list[1:]:
            issues: list[str] = []

            if first.format_name != media.format_name:
                issues.append(
                    f"format_name differs: {first.format_name} vs {media.format_name}"
                )

            if first.video is None and media.video is not None:
                issues.append(
                    "video presence differs: first has no video, this has video"
                )
            elif first.video is not None and media.video is None:
                issues.append(
                    "video presence differs: first has video, this has no video"
                )
            elif first.video is not None and media.video is not None:
                v_first = first.video
                v_media = media.video
                if prop := _prop(
                    label="video.codec",
                    first_value=v_first.codec,
                    value=v_media.codec,
                ):
                    issues.append(prop)
                if prop := _prop(
                    label="video.width",
                    first_value=v_first.width,
                    value=v_media.width,
                ):
                    issues.append(prop)
                if prop := _prop(
                    label="video.height",
                    first_value=v_first.height,
                    value=v_media.height,
                ):
                    issues.append(prop)
                if prop := _prop(
                    label="video.fps", first_value=v_first.fps, value=v_media.fps
                ):
                    issues.append(prop)
                if prop := _prop(
                    label="video.pix_fmt",
                    first_value=v_first.pix_fmt,
                    value=v_media.pix_fmt,
                ):
                    issues.append(prop)

            if first.audio is None and media.audio is not None:
                issues.append(
                    "audio presence differs: first has no audio, this has audio"
                )
            elif first.audio is not None and media.audio is None:
                issues.append(
                    "audio presence differs: first has audio, this has no audio"
                )
            elif first.audio is not None and media.audio is not None:
                if len(first.audio) != len(media.audio):
                    issues.append(
                        "audio track count differs: "
                        f"{len(first.audio)} vs {len(media.audio)}"
                    )
                else:
                    for idx, (a_first, a_media) in enumerate(
                        zip(first.audio, media.audio, strict=True)
                    ):
                        if prop := _prop(
                            label=f"audio[{idx}].codec",
                            first_value=a_first.codec,
                            value=a_media.codec,
                        ):
                            issues.append(prop)
                        if prop := _prop(
                            label=f"audio[{idx}].sample_rate",
                            first_value=a_first.sample_rate,
                            value=a_media.sample_rate,
                        ):
                            issues.append(prop)
                        if prop := _prop(
                            label=f"audio[{idx}].channels",
                            first_value=a_first.channels,
                            value=a_media.channels,
                        ):
                            issues.append(prop)
                        if prop := _prop(
                            label=f"audio[{idx}].channel_layout",
                            first_value=a_first.channel_layout,
                            value=a_media.channel_layout,
                        ):
                            issues.append(prop)

            if issues:
                incompatible.append((media.path, issues))

        if not incompatible:
            return

        lines: list[str] = []
        for path, issues in incompatible:
            lines.append(f"{path}:")
            lines.extend(f"  - {issue}" for issue in issues)

        raise IncompatibleMediaError(
            output=self.params.media_output, incompatible_list=lines
        )
