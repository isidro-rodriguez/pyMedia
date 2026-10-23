"""Comando ``transcode``: service."""

from pymedia.commands.base.service import BaseService
from pymedia.commands.transcode.cmd import TranscodeCmd
from pymedia.commands.transcode.parameters import TranscodeParameters
from pymedia.errors import MissingParameterError
from pymedia.locales import translate as _
from pymedia.mixins.transcode_mixin import is_text_subtitles
from pymedia.models.subtitles import Subtitles
from pymedia.ui import confirm


class TranscodeService(BaseService[TranscodeParameters]):
    """Comando de CLI para transcodificar un contenedor de vídeo."""

    def start(self) -> None:
        """Construye el comando ffmpeg y ejecuta la transcodificación del contenedor.

        Raises:
            MissingParameterError: Si falta el medio o la salida procesada.
        """
        if self.params.media is None:
            raise MissingParameterError(name="media")
        if self.params.media_output is None:
            raise MissingParameterError(name="media_output")

        if not self.resolve_overwrite(output_list=[self.params.media_output]):
            return

        self._resolve_subtitles_compatibility()

        cmd = TranscodeCmd(params=self.params, config=self.config).create()

        self.display_cmd(cmd=cmd)

        self.run_ffmpeg(
            cmd=cmd,
            description=_("Transcoding container"),
            progress_time=self.params.media.duration,
            output_list=[self.params.media_output],
        )

        self.logger.success(
            msg=_("Container transcoded successfully: %(output)s"),
            output=self.params.media_output,
        )

    def _resolve_subtitles_compatibility(self) -> None:
        """Avisa de los subtítulos no admitidos por la salida y decide si convertirlos.

        Los subtítulos gráficos no se pueden convertir y se descartan. Para los
        de texto se pregunta al usuario; con `--show-cmd` se asume la conversión.

        Raises:
            MissingParameterError: Si falta la salida procesada.
        """
        output = self.params.media_output
        if output is None:
            raise MissingParameterError(name="media_output")
        tracks = self.params.incompatible_subtitles(container=output.suffix)
        if not tracks:
            return

        text = [t for t in tracks if is_text_subtitles(t)]
        graphic = [t for t in tracks if not is_text_subtitles(t)]
        if graphic:
            self.logger.warning(
                msg=_(
                    "Graphic subtitles tracks %(tracks)s are not supported by "
                    "%(extension)s and will be discarded."
                ),
                tracks=_format_tracks(graphic),
                extension=output.suffix,
            )
        if text:
            self.logger.warning(
                msg=_(
                    "Subtitles tracks %(tracks)s are not supported by %(extension)s."
                ),
                tracks=_format_tracks(text),
                extension=output.suffix,
            )
            self.params.convert_subtitles = self.show_cmd or confirm(
                _("Convert them to a supported subtitles format?"), default=True
            )
            if not self.params.convert_subtitles:
                self.logger.warning(msg=_("Incompatible subtitles will be discarded."))


def _format_tracks(tracks: list[Subtitles]) -> str:
    """Formatea las pistas como `índice (códec)` separadas por comas."""
    return ", ".join(f"{t.track_index} ({t.format.codec})" for t in tracks)
