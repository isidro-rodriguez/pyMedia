"""Tests de composición del comando ffmpeg del subcomando transcode."""

from pathlib import Path
from unittest.mock import patch

import pytest

from pymedia.commands.transcode.cmd import TranscodeCmd
from pymedia.commands.transcode.parameters import TranscodeParameters
from pymedia.models.config import Config, Transcode
from pymedia.models.media import Audio, Media, Video
from pymedia.types import OverwriteMode
from pymedia.utils import to_ffmpeg_value


@pytest.fixture
def config(tmp_path: Path) -> Config:
    """Config de la plantilla, aislada del `config.toml` del usuario."""
    with patch("platformdirs.user_config_dir", return_value=str(tmp_path)):
        return Config.load()


def _params(
    *,
    subtitles_input: Path | None = None,
    hflip: bool = False,
    with_audio: bool = False,
) -> TranscodeParameters:
    """Construye unos parámetros mínimos con los campos indicados."""
    media_path = Path("/tmp/input.mkv")
    return TranscodeParameters(
        overwrite=OverwriteMode.NO,
        transcode=Transcode(
            video_codec="h265",
            video_preset="medium",
            video_crf=23,
            audio_codec="aac",
            audio_bit_rate="128k",
        ),
        transcode_video=True,
        subtitles_input=subtitles_input,
        media=Media(
            path=media_path,
            video=Video(path=media_path, track_index=0),
            audio=(
                [Audio(path=media_path, language="eng", track_index=0)]
                if with_audio
                else None
            ),
        ),
        media_output=Path("/tmp/out.mkv"),
        hflip=hflip,
    )


def _cmd(params: TranscodeParameters, config: Config) -> list[str]:
    """Comando de ffmpeg compuesto para los parámetros indicados."""
    return TranscodeCmd(params=params, config=config).create()


def _filter_graph(cmd: list[str]) -> str:
    """Devuelve el valor de `-filter_complex` del comando."""
    return cmd[cmd.index("-filter_complex") + 1]


def test_image_filters_build_one_filtergraph(config: Config) -> None:
    """Un filtro de imagen sin subtítulos se compone como hasta ahora."""
    cmd = _cmd(_params(hflip=True), config)

    assert _filter_graph(cmd) == "hflip[v]"
    assert cmd[cmd.index("-map") + 1] == "[v]"


def test_subtitles_build_one_filtergraph(config: Config) -> None:
    """Quemar subtítulos sin otros filtros compone un grafo de un solo filtro."""
    subtitle = Path("/tmp/subs/eng_subs.srt")
    cmd = _cmd(_params(subtitles_input=subtitle), config)

    assert "-vf" not in cmd
    assert _filter_graph(cmd) == f"subtitles={to_ffmpeg_value(subtitle.absolute())}[v]"
    assert cmd[cmd.index("-map") + 1] == "[v]"


def test_subtitles_and_filters_share_the_filtergraph(config: Config) -> None:
    """Subtítulos y filtros van juntos: `-vf` no puede seguir a un grafo complejo."""
    subtitle = Path("/tmp/subs/eng_subs.srt")
    cmd = _cmd(_params(subtitles_input=subtitle, hflip=True), config)

    assert "-vf" not in cmd
    assert _filter_graph(cmd) == (
        f"subtitles={to_ffmpeg_value(subtitle.absolute())},hflip[v]"
    )
    assert cmd[cmd.index("-map") + 1] == "[v]"


def test_conflicting_name_keeps_the_filtergraph_intact(config: Config) -> None:
    """Un nombre con comilla, coma y corchetes se escapa dentro del grafo."""
    subtitle = Path("/tmp/subs/Joan's first bycicle, [2].srt")
    cmd = _cmd(_params(subtitles_input=subtitle, hflip=True), config)

    assert _filter_graph(cmd) == (
        f"subtitles={to_ffmpeg_value(subtitle.absolute())},hflip[v]"
    )
    assert cmd[cmd.index("-map") + 1] == "[v]"


def test_audio_tracks_coexist_with_burned_subtitles(config: Config) -> None:
    """El mapeo de las pistas de audio convive con el vídeo filtrado."""
    cmd = _cmd(
        _params(subtitles_input=Path("/tmp/subs/eng_subs.srt"), with_audio=True),
        config,
    )

    assert "0:a:0" in cmd
    assert "[v]" in cmd


def test_without_filters_maps_the_input_video(config: Config) -> None:
    """Sin filtros no hay grafo complejo y se mapea la pista de vídeo de entrada."""
    cmd = _cmd(_params(), config)

    assert "-filter_complex" not in cmd
    assert cmd[cmd.index("-map") + 1] == "0:v:0"
