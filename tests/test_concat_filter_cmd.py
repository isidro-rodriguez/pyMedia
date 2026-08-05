"""Tests unitarios para concat_filter_cmd (sin ejecutar ffmpeg real)."""

from pathlib import Path
from unittest.mock import patch

import pytest

from pymedia.domain.config import App, Config, ConflictiveJoin, Encode
from pymedia.domain.encode_pipeline import EncodePipeline
from pymedia.domain.media_input import Audio, MediaInput, Video
from pymedia.ffmpeg.concat_filter_cmd import (
    _all_audio_compatible,
    build_audio_chain,
    build_concat_graph,
    build_ffmpeg_command,
    build_input_args,
    build_video_chain,
    concat_filter_cmd,
    determine_targets,
)

# ──────────────────── fixtures ────────────────────


@pytest.fixture
def config() -> Config:
    return Config(
        encode=Encode(
            video_codec="libx264",
            video_preset="medium",
            video_crf=23,
            video_pix_fmt="yuv420p",
            audio_codec="aac",
            audio_bit_rate="128k",
        ),
        conflictive_join=ConflictiveJoin(
            resize_to="min_height",
            fps="max",
            channels="stereo",
            pix_fmt="yuv420p",
            confirm_encode=False,
        ),
        app=App(logger_level="INFO"),
    )


@pytest.fixture
def pipeline() -> EncodePipeline:
    return EncodePipeline()


@pytest.fixture
def media_with_audio() -> MediaInput:
    return MediaInput(
        path=Path("dummy.mp4"),
        video=Video(
            codec="h264", width=640, height=360, fps=30, pix_fmt="yuv420p"
        ),
        audio=Audio(
            codec="aac",
            sample_rate=44100,
            channels=2,
            channel_layout="stereo",
        ),
    )


@pytest.fixture
def media_without_audio() -> MediaInput:
    return MediaInput(
        path=Path("dummy_no_audio.mp4"),
        video=Video(
            codec="h264", width=640, height=360, fps=30, pix_fmt="yuv420p"
        ),
        audio=None,
    )


@pytest.fixture
def target_all_audio() -> dict:
    return {
        "height": 360,
        "fps": "30",
        "pix_fmt": "yuv420p",
        "channel_layout": "stereo",
        "needs_scale": False,
        "needs_fps": False,
        "needs_pix_fmt": False,
        "all_audio_compatible": True,
        "has_audio": True,
    }


# ──────────────── _all_audio_compatible ────────────────


def test_all_audio_compatible_all_with_audio_matching() -> None:
    """Todos con audio y mismo codec/rate/channels/layout → True."""
    medias = [
        MediaInput(
            path=Path("a.mp4"),
            video=Video(),
            audio=Audio(
                codec="aac",
                sample_rate=44100,
                channels=2,
                channel_layout="stereo",
            ),
        ),
        MediaInput(
            path=Path("b.mp4"),
            video=Video(),
            audio=Audio(
                codec="aac",
                sample_rate=44100,
                channels=2,
                channel_layout="stereo",
            ),
        ),
    ]
    assert _all_audio_compatible(medias) is True


def test_all_audio_compatible_some_without_audio() -> None:
    """Alguno sin audio → False."""
    medias = [
        MediaInput(
            path=Path("a.mp4"), video=Video(), audio=Audio(codec="aac")
        ),
        MediaInput(path=Path("b.mp4"), video=Video(), audio=None),
    ]
    assert _all_audio_compatible(medias) is False


def test_all_audio_compatible_all_without_audio() -> None:
    """Todos sin audio → False (no hay audio para comparar)."""
    medias = [
        MediaInput(path=Path("a.mp4"), video=Video(), audio=None),
        MediaInput(path=Path("b.mp4"), video=Video(), audio=None),
    ]
    assert _all_audio_compatible(medias) is False


def test_all_audio_compatible_different_audio() -> None:
    """Todos con audio pero distinto codec → False."""
    medias = [
        MediaInput(
            path=Path("a.mp4"),
            video=Video(),
            audio=Audio(
                codec="aac",
                sample_rate=44100,
                channels=2,
                channel_layout="stereo",
            ),
        ),
        MediaInput(
            path=Path("b.mp4"),
            video=Video(),
            audio=Audio(
                codec="mp3",
                sample_rate=44100,
                channels=2,
                channel_layout="stereo",
            ),
        ),
    ]
    assert _all_audio_compatible(medias) is False


# ──────────────── build_audio_chain ────────────────


def test_build_audio_chain_with_audio_compatible(
    media_with_audio, target_all_audio
) -> None:
    """Audio compatible → solo asetpts."""
    result = build_audio_chain(media_with_audio, 0, target_all_audio)
    assert result == "[0:a]asetpts=PTS-STARTPTS[a0]"


def test_build_audio_chain_with_audio_incompatible(
    media_with_audio,
) -> None:
    """Audio incompatible → normalizar con aresample + aformat."""
    target = {
        "all_audio_compatible": False,
        "channel_layout": "stereo",
    }
    result = build_audio_chain(media_with_audio, 1, target)
    assert "[1:a]aresample=48000" in result
    assert "aformat=sample_fmts=fltp:channel_layouts=stereo" in result
    assert "asetpts=PTS-STARTPTS[a1]" in result


def test_build_audio_chain_without_audio_raises(
    media_without_audio, target_all_audio
) -> None:
    """Sin audio → ValueError (ya no se sintetiza silencio)."""
    with pytest.raises(ValueError, match="Stream de audio no encontrado"):
        build_audio_chain(media_without_audio, 0, target_all_audio)


# ──────────────── build_concat_graph ────────────────


def test_build_concat_graph_with_audio() -> None:
    """Con audio → concat con a=1."""
    result = build_concat_graph(2, has_audio=True)
    assert result == "[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]"


def test_build_concat_graph_without_audio() -> None:
    """Sin audio → concat con a=0."""
    result = build_concat_graph(3, has_audio=False)
    assert result == "[v0][v1][v2]concat=n=3:v=1:a=0[v]"


# ──────────────── build_input_args ────────────────


def test_build_input_args(tmp_path) -> None:
    """Construye los argumentos -i correctamente."""
    paths = [tmp_path / "a.mp4", tmp_path / "b.mp4"]
    paths[0].write_text("")
    paths[1].write_text("")
    medias = [MediaInput(path=p) for p in paths]
    args = build_input_args(medias)
    assert args == [
        "-i",
        str(paths[0].absolute()),
        "-i",
        str(paths[1].absolute()),
    ]


# ──────────────── build_video_chain ────────────────


def test_build_video_chain_no_video_raises() -> None:
    """Sin stream de vídeo → ValueError."""
    media = MediaInput(path=Path("dummy.mp4"), video=None)
    with pytest.raises(ValueError, match="Stream de vídeo no encontrado"):
        build_video_chain(media, 0, {}, EncodePipeline())


def test_build_video_chain_no_scale(media_with_audio) -> None:
    """Sin necesidad de escalado → salida simple."""
    target = {
        "needs_scale": False,
        "needs_fps": False,
        "needs_pix_fmt": False,
    }
    result = build_video_chain(
        media_with_audio, 0, target, EncodePipeline()
    )
    assert result == "[0:v]setsar=1,setpts=PTS-STARTPTS[v0]"


# ──────────────── build_ffmpeg_command ────────────────


def test_build_ffmpeg_command_with_audio(config) -> None:
    """Con audio → incluye -map [a] y -c:a."""
    cmd = build_ffmpeg_command(
        input_args=["-i", "in.mp4"],
        filters="[0:v]...[v0]",
        config=config,
        output="out.mp4",
        has_audio=True,
    )
    assert "-map" in cmd
    assert "[a]" in cmd
    assert "-c:a" in cmd
    assert "aac" in cmd


def test_build_ffmpeg_command_without_audio(config) -> None:
    """Sin audio → no incluye -map [a] ni -c:a."""
    cmd = build_ffmpeg_command(
        input_args=["-i", "in.mp4"],
        filters="[0:v]...[v0]",
        config=config,
        output="out.mp4",
        has_audio=False,
    )
    assert "-map" in cmd
    assert "[a]" not in cmd
    assert "-c:a" not in cmd


# ──────────────── determine_targets ────────────────


def test_determine_targets_has_audio(
    media_with_audio, config, pipeline
) -> None:
    """Con audio → has_audio=True."""
    target = determine_targets([media_with_audio], config, pipeline)
    assert target["has_audio"] is True


def test_determine_targets_has_no_audio(
    media_without_audio, config, pipeline
) -> None:
    """Sin audio → has_audio=False."""
    target = determine_targets([media_without_audio], config, pipeline)
    assert target["has_audio"] is False


def test_determine_targets_mixed_audio(
    config, pipeline, media_with_audio, media_without_audio
) -> None:
    """Mezcla con/sin audio → has_audio=True, all_audio_compatible=False."""
    target = determine_targets(
        [media_with_audio, media_without_audio], config, pipeline
    )
    assert target["has_audio"] is True  # al menos uno tiene audio
    assert target["all_audio_compatible"] is False  # no todos tienen audio


# ──────────────── concat_filter_cmd ────────────────


def test_concat_filter_cmd_all_audio(
    tmp_path, config, media_with_audio
) -> None:
    """Todos con audio → comando incluye audio en el filtro."""
    with patch(
        "pymedia.ffmpeg.concat_filter_cmd.Config.load", return_value=config
    ):
        cmd = concat_filter_cmd(
            [media_with_audio, media_with_audio],
            EncodePipeline(),
            "out.mp4",
        )
    cmd_str = " ".join(cmd)
    assert "a=1" in cmd_str, "El concat graph debe tener a=1"
    assert "-map" in cmd_str
    assert "[a]" in cmd_str


def test_concat_filter_cmd_no_audio(
    tmp_path, config, media_without_audio
) -> None:
    """Ninguno con audio → comando sin audio en el filtro."""
    with patch(
        "pymedia.ffmpeg.concat_filter_cmd.Config.load", return_value=config
    ):
        cmd = concat_filter_cmd(
            [media_without_audio, media_without_audio],
            EncodePipeline(),
            "out.mp4",
        )
    cmd_str = " ".join(cmd)
    assert "a=0" in cmd_str, "El concat graph debe tener a=0"
    assert "[a]" not in cmd_str or "-c:a" not in cmd_str