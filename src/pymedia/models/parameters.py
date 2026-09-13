"""Modelos de parámetros de pipelines."""

from abc import ABC
from dataclasses import dataclass

from pymedia.models.mixins.audio_mixin import AudioInputMixin
from pymedia.models.mixins.filters_mixin import FiltersMixin
from pymedia.models.mixins.fps_mixin import FpsAnimatedMixin, FpsImageMixin
from pymedia.models.mixins.image_mixin import ImageQualityMixin, SceneMixin
from pymedia.models.mixins.media_mixin import MediaInputMixin, MediaListMixin
from pymedia.models.mixins.outputs_mixin import (
    AnimatedOutputMixin,
    AudioOutputMixin,
    ImageOutputMixin,
    MediaOutputMixin,
    SubtitlesOutputMixin,
)
from pymedia.models.mixins.remux_mixin import (
    FastStartMixin,
    RegeneratePtsMixin,
    SortTracksMixin,
)
from pymedia.models.mixins.sheet_presets_mixin import SheetPresetsMixin
from pymedia.models.mixins.streams_mixin import StreamsMixin
from pymedia.models.mixins.subtitles_mixin import SubtitlesInputMixin
from pymedia.models.mixins.timestamps_mixin import (
    TimestampAtMixin,
    TimestampStartEndMixin,
)
from pymedia.models.mixins.transcode_mixin import TranscodeMixin
from pymedia.types import (
    AudioMode,
    OverwriteMode,
    SubtitlesMode,
    ThumbnailsMode,
)


@dataclass(kw_only=True)
class _BaseParameters(ABC):
    """Parámetros base."""

    overwrite: OverwriteMode


@dataclass(kw_only=True)
class AudioParameters(
    _BaseParameters,
    MediaInputMixin,
    MediaOutputMixin,
    AudioInputMixin,
    AudioOutputMixin,
    StreamsMixin,
):
    """Parámetros utilizados por la familia de comandos de audio."""

    audio_mode: AudioMode


@dataclass(kw_only=True)
class AnimatedParameters(
    _BaseParameters,
    MediaInputMixin,
    AnimatedOutputMixin,
    FpsAnimatedMixin,
    FiltersMixin,
    TimestampStartEndMixin,
):
    """Parámetros utilizados por el comando Animated."""


@dataclass(kw_only=True)
class JoinParameters(
    _BaseParameters,
    MediaListMixin,
    MediaOutputMixin,
):
    """Parámetros utilizados por el comando Join."""


@dataclass(kw_only=True)
class InfoParameters(
    _BaseParameters,
    MediaInputMixin,
):
    """Parámetros utilizados por el comando Info."""
    overwrite: OverwriteMode = OverwriteMode.NO


@dataclass(kw_only=True)
class RemuxParameters(
    _BaseParameters,
    MediaInputMixin,
    MediaOutputMixin,
    FastStartMixin,
    RegeneratePtsMixin,
    SortTracksMixin,
):
    """Parámetros utilizados por el comando Remux."""


@dataclass(kw_only=True)
class SheetParameters(
    _BaseParameters,
    MediaInputMixin,
    ImageOutputMixin,
    ImageQualityMixin,
    SheetPresetsMixin,
):
    """Parámetros utilizados por el comando Sheet."""


@dataclass(kw_only=True)
class SplitParameters(
    _BaseParameters,
    MediaInputMixin,
    MediaOutputMixin,
    TimestampAtMixin,
):
    """Parámetros utilizados por el comando Split."""


@dataclass(kw_only=True)
class SubtitlesParameters(
    _BaseParameters,
    MediaInputMixin,
    MediaOutputMixin,
    SubtitlesInputMixin,
    SubtitlesOutputMixin,
    StreamsMixin,
):
    """Parámetros utilizados por la familia de comandos de subtítulos."""

    subtitles_mode: SubtitlesMode


@dataclass(kw_only=True)
class ThumbParameters(
    _BaseParameters,
    MediaInputMixin,
    ImageOutputMixin,
    ImageQualityMixin,
    TimestampAtMixin,
    TimestampStartEndMixin,
    SceneMixin,
    FpsImageMixin,
    FiltersMixin,
):
    """Parámetros utilizados por la familia de comandos de imágenes."""

    thumbnails_mode: ThumbnailsMode


@dataclass(kw_only=True)
class TranscodeParameters(
    _BaseParameters,
    MediaInputMixin,
    MediaOutputMixin,
    StreamsMixin,
    TranscodeMixin,
    FiltersMixin,
):
    """Parámetros utilizados por el comando Transcode."""
