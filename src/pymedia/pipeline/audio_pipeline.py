"""Pipeline de la familia de comandos de audio."""

from pathlib import Path

from pymedia.errors import MissingParameterError
from pymedia.ffmpeg.audio_cmd import AudioCmd
from pymedia.locales import _  # noqa
from pymedia.models.media import Media
from pymedia.models.parameters import AudioParameters
from pymedia.pipeline.base_pipeline import BasePipeline
from pymedia.types import AudioMode, OverwriteMode, StreamsMode


class AudioPipeline(BasePipeline[AudioParameters]):
    """Comando de CLI que manipula las pistas de audio de un vídeo."""

    def process_parameters(
        self,
        media_input: Path,
        overwrite: OverwriteMode,
        audio_mode: AudioMode,
        audio_input: Path | None = None,
        audio_language: str | None = None,
        media_output: Path | None = None,
        audio_title: str | None = None,
        audio_forced: bool = False,
        audio_default: bool = False,
        audio_hearing_impaired: bool = False,
        audio_commentary: bool = False,
        audio_stream_tracks: str | None = None,
        audio_output: Path | None = None,
    ) -> None:
        """Valida y parsea los argumentos en parámetros procesados."""
        params = AudioParameters(
            overwrite=overwrite,
            audio_mode=audio_mode,
        )

        params.create_media_input(
            media_input=media_input,
            logger=self.logger,
        )

        match audio_mode:
            case AudioMode.ADD:
                if audio_input is None:
                    raise MissingParameterError(name="audio_input")
                params.create_media_output(
                    extension=media_input.suffix,
                    affix="_added_audio",
                    output=media_output,
                )
                params.create_add_audio(
                    audio_input=audio_input.absolute(),
                    language=audio_language,
                    logger=self.logger,
                    title=audio_title,
                    forced=audio_forced,
                    default=audio_default,
                    hearing_impaired=audio_hearing_impaired,
                    commentary=audio_commentary,
                )
            case AudioMode.DELETE:
                params.create_streams(
                    stream_tracks=self._resolve_tracks(
                        media=params.media,
                        stream_tracks=audio_stream_tracks,
                    ),
                    streams_type=StreamsMode.AUDIO,
                )
                params.create_media_output(
                    extension=media_input.suffix,
                    affix="_deleted_audio",
                    output=media_output,
                )
            case AudioMode.EXTRACT:
                params.create_streams(
                    stream_tracks=self._resolve_tracks(
                        media=params.media,
                        stream_tracks=audio_stream_tracks,
                    ),
                    streams_type=StreamsMode.AUDIO,
                )
                params.create_audio_output(
                    extension=self.config.default_containers.audio_track,
                    affix="_extracted_audio",
                    output=audio_output,
                )
            case AudioMode.EDIT:
                if audio_stream_tracks is None:
                    raise MissingParameterError(name="audio_stream_tracks")
                params.create_media_output(
                    extension=media_input.suffix,
                    affix="_edited_audio",
                    output=media_output,
                )
                params.create_streams(
                    stream_tracks=audio_stream_tracks,
                    streams_type=StreamsMode.AUDIO,
                )
                params.create_edit_audio(
                    language=audio_language,
                    title=audio_title,
                    forced=audio_forced,
                    default=audio_default,
                    hearing_impaired=audio_hearing_impaired,
                    commentary=audio_commentary,
                )

        self.params = params

    def process_cmd(self) -> None:
        """Construye el comando ffmpeg y ejecuta la manipulación de audio."""
        if self.params.media is None:
            raise MissingParameterError(name="media")
        if self.params.media_output is None:
            raise MissingParameterError(name="media_output")

        audio_cmd = AudioCmd(params=self.params)
        match self.params.audio_mode:
            case AudioMode.ADD:
                cmd = audio_cmd.create_add_audio_cmd()
                if not self.resolve_overwrite(output_list=[self.params.media_output]):
                    return
                description = _("Adding audio")
                success = _("Audio added successfully: %(output)s")
            case AudioMode.DELETE:
                cmd = audio_cmd.create_delete_audio_cmd()
                if not self.resolve_overwrite(output_list=[self.params.media_output]):
                    return
                description = _("Deleting audio")
                success = _("Audio deleted successfully: %(output)s")
            case AudioMode.EDIT:
                cmd = audio_cmd.create_edit_audio_cmd()
                if not self.resolve_overwrite(output_list=[self.params.media_output]):
                    return
                description = _("Editing audio metadata")
                success = _("Audio metadata edited successfully: %(output)s")
            case AudioMode.EXTRACT:
                cmd, output_list = audio_cmd.create_extract_audio_cmd()
                if not self.resolve_overwrite(output_list=output_list):
                    return
                description = _("Extracting audio")
                success = _("Audio extracted successfully: %(output)s")

        self.logger.debug(_("FFmpeg command: %(cmd)s"), cmd=cmd)

        self.run_ffmpeg(cmd=cmd, description=description)

        output = self.params.media_output or self.params.audio_output
        self.logger.info(msg=success, output=output)

    @staticmethod
    def _resolve_tracks(media: Media | None, stream_tracks: str | None) -> str:
        """Resuelve el listado de pistas; sin listado, selecciona todas."""
        if stream_tracks is not None:
            return stream_tracks
        if media is None:
            raise MissingParameterError(name="media")
        if not media.audio:
            raise MissingParameterError(name=_("audio"))
        return ",".join(str(track.track_index) for track in media.audio)
