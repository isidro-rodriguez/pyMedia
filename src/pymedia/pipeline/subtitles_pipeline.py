"""Pipeline de la familia de comandos de subtítulos."""

from pathlib import Path

from pymedia.errors import MissingParameterError, SubtitlesError
from pymedia.ffmpeg.subtitles_cmd import SubtitlesCmd
from pymedia.locales import _  # noqa
from pymedia.models.media import Media
from pymedia.models.parameters import SubtitlesParameters
from pymedia.pipeline.base_pipeline import BasePipeline
from pymedia.types import OverwriteMode, StreamsMode, SubtitlesMode


class SubtitlesPipeline(BasePipeline[SubtitlesParameters]):
    """Comando de CLI que manipula las pistas de subtítulos de un vídeo."""

    def process_parameters(
        self,
        media_input: Path,
        overwrite: OverwriteMode,
        subtitles_mode: SubtitlesMode,
        subtitles_input: Path | None = None,
        subtitles_language: str | None = None,
        media_output: Path | None = None,
        subtitles_title: str | None = None,
        subtitles_forced: bool = False,
        subtitles_default: bool = False,
        subtitles_hearing_impaired: bool = False,
        subtitles_visual_impaired: bool = False,
        subtitles_stream_tracks: str | None = None,
        subtitles_output: Path | None = None,
    ) -> None:
        """Valida y parsea los argumentos en parámetros procesados."""
        params = SubtitlesParameters(
            overwrite=overwrite,
            subtitles_mode=subtitles_mode,
        )

        params.create_media_input(
            media_input=media_input,
            logger=self.logger,
        )

        match subtitles_mode:
            case SubtitlesMode.ADD:
                if subtitles_input is None:
                    raise MissingParameterError(name="subtitles_input")
                params.create_media_output(
                    extension=media_input.suffix,
                    affix="_added_subs",
                    output=media_output,
                )
                params.create_add_subtitles(
                    subtitles_input=subtitles_input.absolute(),
                    language=subtitles_language,
                    logger=self.logger,
                    title=subtitles_title,
                    forced=subtitles_forced,
                    default=subtitles_default,
                    hearing_impaired=subtitles_hearing_impaired,
                    visual_impaired=subtitles_visual_impaired,
                )
            case SubtitlesMode.DELETE:
                params.create_streams(
                    stream_tracks=self._resolve_tracks(
                        media=params.media,
                        stream_tracks=subtitles_stream_tracks,
                    ),
                    streams_type=StreamsMode.SUBTITLES,
                )
                params.create_media_output(
                    extension=media_input.suffix,
                    affix="_deleted_subs",
                    output=media_output,
                )
            case SubtitlesMode.EXTRACT:
                params.create_streams(
                    stream_tracks=self._resolve_tracks(
                        media=params.media,
                        stream_tracks=subtitles_stream_tracks,
                    ),
                    streams_type=StreamsMode.SUBTITLES,
                )
                params.create_subtitles_output(
                    extension=self.config.default_containers.subtitles,
                    affix="_extracted_subs",
                    output=subtitles_output,
                )
            case SubtitlesMode.EDIT:
                if subtitles_stream_tracks is None:
                    raise MissingParameterError(name="subtitles_stream_tracks")
                params.create_media_output(
                    extension=media_input.suffix,
                    affix="_edited_subs",
                    output=media_output,
                )
                params.create_streams(
                    stream_tracks=subtitles_stream_tracks,
                    streams_type=StreamsMode.SUBTITLES,
                )
                params.create_edit_subtitles(
                    language=subtitles_language,
                    title=subtitles_title,
                    forced=subtitles_forced,
                    default=subtitles_default,
                    hearing_impaired=subtitles_hearing_impaired,
                    visual_impaired=subtitles_visual_impaired,
                )

        self.params = params

    def process_cmd(self) -> None:
        """Construye el comando ffmpeg y ejecuta la manipulación de subtítulos."""
        if self.params.media is None:
            raise MissingParameterError(name="media")
        if self.params.media_output is None:
            raise MissingParameterError(name="media_output")

        sub_cmd = SubtitlesCmd(params=self.params)
        match self.params.subtitles_mode:
            case SubtitlesMode.ADD:
                cmd = sub_cmd.create_add_subtitles_cmd()
                if not self.resolve_overwrite(output_list=[self.params.media_output]):
                    return
                description = _("Adding subtitles")
                success = _("Subtitles added successfully: %(output)s")
            case SubtitlesMode.DELETE:
                cmd = sub_cmd.create_delete_subtitles_cmd()
                if not self.resolve_overwrite(output_list=[self.params.media_output]):
                    return
                description = _("Deleting subtitles")
                success = _("Subtitles deleted successfully: %(output)s")
            case SubtitlesMode.EDIT:
                cmd = sub_cmd.create_edit_subtitles_cmd()
                if not self.resolve_overwrite(output_list=[self.params.media_output]):
                    return
                description = _("Editing subtitles metadata")
                success = _("Subtitles metadata edited successfully: %(output)s")
            case SubtitlesMode.EXTRACT:
                cmd, output_list = sub_cmd.create_extract_subtitles_cmd()
                if not self.resolve_overwrite(output_list=output_list):
                    return
                description = _("Extracting subtitles")
                success = _("Subtitles extracted successfully: %(output)s")

        self.logger.debug(_("FFmpeg command: %(cmd)s"), cmd=cmd)

        self.run_ffmpeg(cmd=cmd, description=description)

        output = self.params.media_output or self.params.subtitles_output
        self.logger.info(msg=success, output=output)

    @staticmethod
    def _resolve_tracks(media: Media | None, stream_tracks: str | None) -> str:
        """Resuelve el listado de pistas; sin listado, selecciona todas."""
        if stream_tracks is not None:
            return stream_tracks
        if media is None:
            raise MissingParameterError(name="media")
        if not media.subtitles:
            raise SubtitlesError(
                msg=_("The media file does not contain subtitles streams.")
            )
        return ",".join(str(track.track_index) for track in media.subtitles)
