"""Modelos de parámetros de pipelines."""

from dataclasses import dataclass

from pymedia.models.mixins.audio_mixin import AudioInputMixin
from pymedia.models.mixins.crop_mixin import CropMixin
from pymedia.models.mixins.flip_mixin import FlipMixin
from pymedia.models.mixins.fps_mixin import FpsGifMixin, FpsImageMixin
from pymedia.models.mixins.image_mixin import ImageQualityMixin, SceneMixin
from pymedia.models.mixins.media_mixin import MediaInputMixin
from pymedia.models.mixins.outputs_mixin import (
    AnimatedOutputMixin,
    AudioOutputMixin,
    ImageOutputMixin,
    MediaOutputMixin,
    SubtitlesOutputMixin,
)
from pymedia.models.mixins.rotate_mixin import RotateMixin
from pymedia.models.mixins.scale_mixin import ScaleMixin
from pymedia.models.mixins.sheet_presets_mixin import SheetPresetsMixin
from pymedia.models.mixins.streams_mixin import StreamsMixin
from pymedia.models.mixins.subtitles_mixin import SubtitlesInputMixin
from pymedia.models.mixins.timestamps_mixin import (
    TimestampAtMixin,
    TimestampStartEndMixin,
)
from pymedia.types import AudioMode, OverwriteMode, SubtitlesMode


@dataclass(kw_only=True)
class AudioParameters(
    MediaInputMixin,
    MediaOutputMixin,
    AudioInputMixin,
    AudioOutputMixin,
    StreamsMixin,
):
    """Parámetros validados y parseados para la manipulación de subtítulos."""

    overwrite: OverwriteMode
    audio_mode: AudioMode


@dataclass(kw_only=True)
class GifParameters(
    MediaInputMixin,
    AnimatedOutputMixin,
    FpsGifMixin,
    CropMixin,
    ScaleMixin,
    FlipMixin,
    RotateMixin,
    TimestampStartEndMixin,
):
    """Parámetros utilizados por el comando GIF."""

    overwrite: OverwriteMode


@dataclass(kw_only=True)
class InfoParameters(
    MediaInputMixin,
):
    """Parámetros utilizados por el comando Info."""


@dataclass(kw_only=True)
class SheetParameters(
    MediaInputMixin,
    ImageOutputMixin,
    ImageQualityMixin,
    SheetPresetsMixin,
):
    """Parámetros utilizados por el comando Sheet."""

    overwrite: OverwriteMode


@dataclass(kw_only=True)
class SubtitlesParameters(
    MediaInputMixin,
    MediaOutputMixin,
    SubtitlesInputMixin,
    SubtitlesOutputMixin,
    StreamsMixin,
):
    """Parámetros validados y parseados para la manipulación de subtítulos."""

    overwrite: OverwriteMode
    subtitles_mode: SubtitlesMode


@dataclass(kw_only=True)
class ThumbParameters(
    MediaInputMixin,
    ImageOutputMixin,
    ImageQualityMixin,
    TimestampAtMixin,
    TimestampStartEndMixin,
    SceneMixin,
    FpsImageMixin,
    CropMixin,
    ScaleMixin,
    FlipMixin,
    RotateMixin,
):
    """Parámetros validados y parseados para generar capturas de vídeo."""

    overwrite: OverwriteMode
