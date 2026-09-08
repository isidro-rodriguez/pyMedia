"""Tests de composición de comandos ffmpeg de la familia de subtítulos."""

from pathlib import Path

from pymedia.ffmpeg.subtitles_cmd import SubtitlesCmd
from pymedia.models.media import Media
from pymedia.models.parameters import SubtitlesParameters
from pymedia.models.subtitles import Subtitles
from pymedia.types import OverwriteMode, SubtitlesMode


def _params(
    mode: SubtitlesMode,
    *,
    stream_tracks: list[int] | None = None,
    media_output: Path | None = None,
    subtitles_output: Path | None = None,
    subtitles: Subtitles | None = None,
    media_subtitles: list[Subtitles] | None = None,
) -> SubtitlesParameters:
    """Construye unos parámetros mínimos con el modo y los campos indicados."""
    return SubtitlesParameters(
        overwrite=OverwriteMode.NO,
        subtitles_mode=mode,
        media=Media(path=Path("/tmp/input.mkv"), subtitles=media_subtitles),
        media_output=media_output,
        subtitles_output=subtitles_output,
        stream_tracks=stream_tracks,
        subtitles=subtitles,
    )


def _disposition_value(cmd: list[str], flag: str) -> str:
    """Devuelve el valor que acompaña a un flag `-disposition` del comando."""
    return cmd[cmd.index(flag) + 1]


def test_delete_maps_by_subtitle_local_index() -> None:
    """Delete renderiza `-0:s:N` (índice local), no `-0:N` (global)."""
    params = _params(
        SubtitlesMode.DELETE,
        stream_tracks=[0, 2],
        media_output=Path("/tmp/out.mkv"),
    )

    cmd = SubtitlesCmd(params=params).create()

    assert "-0:s:0" in cmd
    assert "-0:s:2" in cmd
    assert not any(mapping in cmd for mapping in ("-0:0", "-0:2"))


def test_extract_maps_by_subtitle_local_index() -> None:
    """Extract renderiza `0:s:N` (índice local) dentro de la entrada 0."""
    params = _params(
        SubtitlesMode.EXTRACT,
        stream_tracks=[0, 1],
        subtitles_output=Path("/tmp/out.srt"),
    )

    cmd = SubtitlesCmd(params=params).create()

    assert "0:s:0" in cmd
    assert "0:s:1" in cmd
    assert not any(mapping in cmd for mapping in ("0:0", "0:1"))


def test_add_encodes_new_subtitle_with_local_index() -> None:
    """Add codifica el nuevo subtítulo con `-c:s:N` (índice local)."""
    params = _params(
        SubtitlesMode.ADD,
        media_output=Path("/tmp/out.mkv"),
        subtitles=Subtitles(
            path=Path("/tmp/subs.srt"),
            track_index=2,
            codec="srt",
            language="spa",
            title="Español",
            forced=False,
            default=False,
        ),
    )

    cmd = SubtitlesCmd(params=params).create()

    assert "-c:s:2" in cmd
    assert "srt" in cmd
    # La metadata exige la forma `s:s:N` (tipo + índice local): con `s:N`
    # el índice se interpreta como global y etiqueta la pista equivocada.
    assert "-metadata:s:s:2" in cmd
    assert "language=spa" in cmd
    assert "title=Español" in cmd
    assert "-metadata:s:2" not in cmd


def test_edit_default_is_exclusive() -> None:
    """Edit marca `default` en la pista editada y lo retira de las demás."""
    media_subtitles = [
        Subtitles(
            path=Path("/tmp/input.mkv"), track_index=0, default=True, forced=True
        ),
        Subtitles(path=Path("/tmp/input.mkv"), track_index=1),
        Subtitles(path=Path("/tmp/input.mkv"), track_index=2, default=True),
    ]
    params = _params(
        SubtitlesMode.EDIT,
        stream_tracks=[2],
        media_output=Path("/tmp/out.mkv"),
        media_subtitles=media_subtitles,
        subtitles=Subtitles(
            path=Path("/tmp/input.mkv"),
            track_index=2,
            default=True,
        ),
    )

    cmd = SubtitlesCmd(params=params).create()

    assert _disposition_value(cmd, "-disposition:s:2") == "default"
    # La pista 0 era `default+forced`: conserva `forced`, pierde `default`.
    assert _disposition_value(cmd, "-disposition:s:0") == "forced"
    # La pista 1 no era default: no se toca.
    assert "-disposition:s:1" not in cmd


def test_edit_without_default_leaves_others_untouched() -> None:
    """Edit sin `--default` no emite disposiciones sobre las demás pistas."""
    media_subtitles = [
        Subtitles(path=Path("/tmp/input.mkv"), track_index=0, default=True),
        Subtitles(path=Path("/tmp/input.mkv"), track_index=1),
    ]
    params = _params(
        SubtitlesMode.EDIT,
        stream_tracks=[1],
        media_output=Path("/tmp/out.mkv"),
        media_subtitles=media_subtitles,
        subtitles=Subtitles(
            path=Path("/tmp/input.mkv"),
            track_index=1,
            default=False,
        ),
    )

    cmd = SubtitlesCmd(params=params).create()

    assert "-disposition:s:0" not in cmd
