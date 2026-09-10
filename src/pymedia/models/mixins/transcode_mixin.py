"""Mixin de transcodificación."""

from dataclasses import dataclass
from typing import Protocol

from pymedia.models.media import Media
from pymedia.types import PresetsTranscodeMode


class _TranscodeContext(Protocol):
    media: Media
    stream_tracks: list[int] | None = None


@dataclass(kw_only=True)
class TranscodeMixin(_TranscodeContext):
    """Mixin para los parámetros de transcodificación.

    Attributes:
        preset_transcode: Perfiles de transcodificación presente en config.toml.
        transcode_video: Permite la transcodificación de la pista de video.
    """

    preset_transcode: PresetsTranscodeMode = PresetsTranscodeMode.EVEN
    transcode_video: bool = False
    transcode_audio: list[int] | None = None

    def create_transcode(self, mode: PresetsTranscodeMode, video: bool) -> None:
        """Establece los parámetros de transcodificación.

        Args:
            mode: Preset de transcodificación.
            video: Permite la transcodificación de la pista de video.
        """
        self.preset_transcode = mode
        self.transcode_video = video
