"""Comando ``join``: service."""

import tempfile
from pathlib import Path

from pymedia.commands.base.service import BaseService
from pymedia.commands.join.cmd import JoinCmd
from pymedia.commands.join.parameters import JoinParameters
from pymedia.errors import MissingParameterError, UserError
from pymedia.locales import translate as _
from pymedia.models.media import Media

# Propiedades de formato que deben coincidir para unir sin transcodificar.
_VIDEO_PROPS = ("codec", "width", "height", "fps", "pix_fmt")
_AUDIO_PROPS = ("codec", "sample_rate", "channels", "channel_layout")


class JoinService(BaseService[JoinParameters]):
    """Comando de CLI para la unión de múltiples contenedores."""

    def start(self) -> None:
        """Construye el comando ffmpeg y ejecuta la unión de los ficheros multimedia.

        Raises:
            MissingParameterError: Si falta el listado o la salida del medio.
            UserError: Si algún medio de la lista no es compatible con el primero.
        """
        if self.params.media_list is None:
            raise MissingParameterError(name="media_list")
        if self.params.media_output is None:
            raise MissingParameterError(name="media_output")

        self._check_media_compatibility()

        if not self.resolve_overwrite(output_list=[self.params.media_output]):
            return

        with tempfile.TemporaryDirectory() as tmp_dir:
            list_txt = Path(tmp_dir) / "list.txt"
            _write_concat_list(list_txt=list_txt, media_list=self.params.media_list)
            cmd = JoinCmd(params=self.params).create(list_txt=list_txt)

            self.logger.debug(
                _("List file:\n%(list_txt)s"), list_txt=list_txt.read_text()
            )

            self.display_cmd(cmd=cmd)

            self.run_ffmpeg(
                cmd=cmd,
                description=_("Joining media files"),
                output_list=[self.params.media_output],
            )

        self.logger.info(
            msg=_("Containers joined successfully: %(output)s"),
            output=self.params.media_output,
        )

    def _check_media_compatibility(self) -> None:
        """Comprueba que todos los vídeos de la lista son compatibles con el primero.

        Raises:
            MissingParameterError: Si falta la salida del medio.
            UserError: Si algún medio de la lista no es compatible con el primero.
        """
        if self.params.media_output is None:
            raise MissingParameterError(name="media_output")
        if self.params.media_list is None or len(self.params.media_list) < 2:
            return

        first, *others = self.params.media_list
        lines: list[str] = []
        for media in others:
            if issues := _video_issues(first, media) + _audio_issues(first, media):
                lines.append(f"{media.path}:")
                lines.extend(f"  - {issue}" for issue in issues)

        if lines:
            raise UserError(
                msg=_(
                    "Incompatible media files for join output %(output)s.\n"
                    "Incompatibilities:\n%(incompatible_list)s"
                )
                % {
                    "output": self.params.media_output,
                    "incompatible_list": "\n".join(lines),
                }
            )


def _write_concat_list(list_txt: Path, media_list: list[Media]) -> None:
    """Escribe el fichero de entrada del demuxer `concat` de ffmpeg."""
    with list_txt.open(mode="w", encoding="utf-8", newline="\n") as file:
        for media in media_list:
            # Siempre entre comillas: `#`, `\` o espacios rompen el demuxer.
            escaped = media.path.as_posix().replace("'", "'\\''")
            file.write(f"file '{escaped}'\n")


def _presence_issue(kind: str, first: object | None, other: object | None) -> list[str]:
    """Describe la diferencia si solo uno de los dos medios tiene el tipo `kind`."""
    if (first is None) == (other is None):
        return []
    if first is None:
        return [f"{kind} presence differs: first has no {kind}, this has {kind}"]
    return [f"{kind} presence differs: first has {kind}, this has no {kind}"]


def _diff_props(
    label: str, first: object, other: object, props: tuple[str, ...]
) -> list[str]:
    """Lista las propiedades de formato que difieren entre dos pistas."""
    issues: list[str] = []
    for prop in props:
        first_value, value = getattr(first, prop), getattr(other, prop)
        if first_value != value:
            issues.append(f"{label}.{prop} differs: {first_value} vs {value}")
    return issues


def _video_issues(first: Media, media: Media) -> list[str]:
    """Diferencias de la pista de vídeo de `media` respecto a `first`."""
    if first.video is None or media.video is None:
        return _presence_issue("video", first.video, media.video)
    return _diff_props("video", first.video.format, media.video.format, _VIDEO_PROPS)


def _audio_issues(first: Media, media: Media) -> list[str]:
    """Diferencias de las pistas de audio de `media` respecto a `first`."""
    if first.audio is None or media.audio is None:
        return _presence_issue("audio", first.audio, media.audio)
    if len(first.audio) != len(media.audio):
        return [f"audio track count differs: {len(first.audio)} vs {len(media.audio)}"]
    return [
        issue
        for idx, (a_first, a_media) in enumerate(
            zip(first.audio, media.audio, strict=True)
        )
        for issue in _diff_props(
            f"audio[{idx}]", a_first.format, a_media.format, _AUDIO_PROPS
        )
    ]
