"""Funciones factory reutilizables para construir objetos en los tests."""

from datetime import timedelta
from fractions import Fraction

from pymedia.models.config import App, Config, ConflictiveJoin, Encode
from pymedia.models.media import Audio, Media, Video


def make_media(
    *,
    duration: timedelta | None = timedelta(seconds=60),
    video: Video | None = None,
    audio: Audio | None = None,
) -> Media:
    """Construye un objeto Media con valores por defecto."""
    return Media(duration=duration, video=video, audio=audio)


def make_video(
    *,
    codec: str | None = "h264",
    width: int | None = 1920,
    height: int | None = 1080,
    fps: Fraction | None = Fraction(25, 1),
    bit_rate: int | None = 1000000,
    pix_fmt: str | None = "yuv420p",
    aspect_ratio: str | None = "16:9",
) -> Video:
    """Construye un objeto Video con valores por defecto."""
    return Video(
        codec=codec,
        width=width,
        height=height,
        fps=fps,
        bit_rate=bit_rate,
        pix_fmt=pix_fmt,
        aspect_ratio=aspect_ratio,
    )


def make_audio(
    *,
    codec: str | None = "aac",
    sample_rate: int | None = 48000,
    channels: int | None = 2,
    channel_layout: str | None = "stereo",
    bit_rate: int | None = 128000,
    language: str | None = "eng",
) -> Audio:
    """Construye un objeto Audio con valores por defecto."""
    return Audio(
        codec=codec,
        sample_rate=sample_rate,
        channels=channels,
        channel_layout=channel_layout,
        bit_rate=bit_rate,
        language=language,
    )


def make_config(
    *,
    video_codec: str = "h264",
    video_preset: str = "medium",
    video_crf: int = 23,
    audio_codec: str = "aac",
    audio_bit_rate: str = "128k",
    default_container: str = ".mp4",
    resize_to: str = "min_height",
    fps: str = "min_fps",
    channels: str = "stereo",
    confirm_encode: bool = True,
    language: str = "english",
    disable_resolution_increase: bool = True,
) -> Config:
    """Construye un Config con valores por defecto."""
    return Config(
        encode=Encode(
            video_codec=video_codec,
            video_preset=video_preset,
            video_crf=video_crf,
            audio_codec=audio_codec,
            audio_bit_rate=audio_bit_rate,
            default_container=default_container,
        ),
        conflictive_join=ConflictiveJoin(
            resize_to=resize_to,
            fps=fps,
            channels=channels,
            confirm_encode=confirm_encode,
        ),
        app=App(
            language=language,
            disable_resolution_increase=disable_resolution_increase,
        ),
    )


def reset_state(config: Config | None = None):
    """Limpia el state global (singleton) y devuelve la instancia.

    Los módulos importan `state` por referencia, por lo que se muta el objeto
    existente en lugar de reasignar el atributo del módulo.
    """
    import pymedia.models.state as state_module

    state = state_module.state
    state.config = config or make_config()
    state.local = "en"
    state.arguments = None
    state.inputs = []
    state.media = []
    state.video_pipeline = None
    state.gif_pipeline = None
    state.output = None
    state.output_on_conflict = None
    return state