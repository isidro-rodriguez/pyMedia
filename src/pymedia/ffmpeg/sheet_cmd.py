import locale
from datetime import timedelta
from fractions import Fraction
from pathlib import Path

from pymedia.errors import (
    CommandGenerationError,
    MissingMediaError,
    MissingMediaPropertyError,
    MissingParameterError,
)
from pymedia.models.media import Audio, Subtitle
from pymedia.models.pipeline.sheet_pipeline import SheetParameters

# Funciones auxiliares
# -----------------------------------------------------------------------------


def _escape_drawtext(text: str) -> str:
    text = text.replace("\\", "\\\\")
    text = text.replace(":", "\\:")
    text = text.replace("%", "\\%")
    text = text.replace("'", r"'\''")
    return text


def _build_duration_display(time: timedelta) -> str:
    total = int(time.total_seconds())
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


# Generar cuadrícula de capturas
# -----------------------------------------------------------------------------


def _generate_snapshots(params: SheetParameters, output: Path) -> list[str]:
    def _calculate_capture_frames() -> list[int]:
        start = int(total_frames * 0.05)
        end = int(total_frames * 0.95)
        step = (end - start) / n_captures
        return [start + int(step * i) for i in range(n_captures)]

    def _build_thumb_pad() -> str:
        if params.preset is None:
            raise MissingParameterError(name="preset")
        bw = params.preset.border_width
        half_gap = params.preset.gap // 2
        border = (
            f"pad=iw+{bw * 2}:ih+{bw * 2}:{bw}:{bw}:color={params.preset.border_color}"
        )
        gap = (
            f"pad=iw+{half_gap * 2}:ih+{half_gap * 2}:"
            f"{half_gap}:{half_gap}:color={params.preset.background}"
        )
        return f"{border},{gap}"

    def _build_timestamp_drawtext() -> str:
        if params.preset is None:
            raise MissingParameterError(name="preset")
        ts_margin = 4
        return (
            f"drawtext=fontfile={params.preset.fontfile.as_posix()}:"
            f"text='{_escape_drawtext(timestamp_str)}':"
            f"fontsize={params.preset.timestamp_fontsize}:"
            f"fontcolor={params.preset.timestamp_color}:"
            f"bordercolor={params.preset.timestamp_border_color}:"
            f"borderw={params.preset.timestamp_border_width}:"
            f"x=w-tw-{ts_margin}:y=h-th-{ts_margin}"
        )

    def _build_stack_filter() -> str:
        if params.preset is None:
            raise MissingParameterError(name="preset")
        rows_expr = []
        for row in range(params.preset.rows):
            inputs = "".join(f"[t{row}{col}]" for col in range(params.preset.columns))
            rows_expr.append(f"{inputs}hstack=inputs={params.preset.columns}[row{row}]")
        row_labels = "".join(f"[row{row}]" for row in range(params.preset.rows))
        rows_expr.append(f"{row_labels}vstack=inputs={params.preset.rows}[grid]")
        return ";".join(rows_expr)

    preset = params.preset
    media = params.media

    if preset is None:
        raise MissingParameterError(name="preset")
    if params.input_single is None:
        raise MissingParameterError(name="input_single")
    if media is None:
        raise MissingMediaError(path=str(params.input_single))
    if media.duration is None:
        raise MissingMediaPropertyError(name="duration")
    if media.video is None or media.video.fps is None:
        raise MissingMediaPropertyError(name="fps")

    total_frames = int(media.duration.total_seconds() * media.video.fps)
    n_captures = preset.columns * preset.rows
    frames = _calculate_capture_frames()

    split_labels = "".join(f"[s{i}]" for i in range(n_captures))
    filter_complex_parts = [f"split={n_captures}{split_labels}"]

    for i, frame_n in enumerate(frames):
        r, c = divmod(i, preset.columns)
        seconds = timedelta(
            microseconds=round((Fraction(frame_n) / media.video.fps) * 1_000_000)
        )
        timestamp_str = _build_duration_display(seconds)

        filter_complex_parts.append(
            f"[s{i}]select='eq(n\\,{frame_n})',"
            f"scale={params.thumb_width}:-1,"
            f"{_build_timestamp_drawtext()},"
            f"{_build_thumb_pad()}[t{r}{c}]"
        )

    filter_complex_parts.append(_build_stack_filter())

    m = preset.margin
    filter_complex_parts.append(
        f"[grid]pad=iw+{m * 2}:ih+{m * 2}:{m}:{m}:color={preset.background}[out]"
    )

    return [
        "ffmpeg",
        "-y",
        "-i",
        str(params.input_single),
        "-filter_complex",
        ";".join(filter_complex_parts),
        "-map",
        "[out]",
        "-frames:v",
        "1",
        str(output),
    ]


# Generar cabecera con metadatos
# -----------------------------------------------------------------------------


def _generate_header(params: SheetParameters, input_single: Path) -> list[str]:
    def _truncate_list_display(prefix: str, items: list[str], max_len: int) -> str:
        base_template = f"{prefix} [{', '.join(items)}]"
        if len(base_template) <= max_len:
            return base_template

        acc = []
        for item in items:
            candidate = f"{prefix} [{', '.join(acc + [item])}, ...]"
            if len(candidate) > max_len:
                break
            acc.append(item)

        if not acc:
            return f"{prefix} [...]"

        return f"{prefix} [{', '.join(acc)}, ...]"

    def _build_size_display(size_bytes: int) -> str:
        def _format_number(value: float | int, decimals: int = 0) -> str:
            fmt = f"%.{decimals}f" if decimals > 0 else "%.0f"
            return locale.format_string(fmt, value, grouping=True)

        size_gb = size_bytes / (1024**3)
        size_mb = size_bytes / (1024**2)
        bytes_str = _format_number(size_bytes)

        if size_gb >= 1.0:
            gb_str = _format_number(size_gb, 2)
            return f"{gb_str} GB ({bytes_str} bytes)"

        mb_str = _format_number(size_mb, 2)
        return f"{mb_str} MB ({bytes_str} bytes)"

    def _build_audio_line(tracks: list[Audio], max_len: int) -> str | None:
        def _format_channels(channels: int) -> str:
            mapping = {1: "mono", 2: "stereo", 6: "5.1", 8: "7.1"}
            return mapping.get(channels, f"{channels}ch")

        if not tracks:
            return None

        formatted_items = []
        for t in tracks:
            if t.channels is None:
                raise MissingParameterError(name="track channels")
            if t.language is None:
                raise MissingParameterError(name="track language")
            if t.codec is None:
                raise MissingParameterError(name="track codec")
            ch_str = _format_channels(t.channels)
            formatted_items.append(f"{t.language} ({t.codec} {ch_str})")

        prefix = f"Audio: {len(tracks)} tracks"
        return _truncate_list_display(prefix, formatted_items, max_len)

    def _build_subtitles_line(subtitles: list[Subtitle], max_len: int) -> str | None:
        if not subtitles:
            return None

        subs: list[str] = []
        for sub in subtitles:
            if sub.language is None:
                raise MissingParameterError(name="subtitle language")
            subs.append(sub.language)

        prefix = f"Subtitles: {len(subtitles)} tracks"
        return _truncate_list_display(prefix, subs, max_len)

    preset = params.preset
    media = params.media

    if params.input_single is None:
        raise MissingParameterError(name="input_single")
    if params.output is None:
        raise MissingParameterError(name="output")
    if preset is None:
        raise MissingParameterError(name="preset")
    if media is None:
        raise MissingMediaError(path=str(params.input_single))
    if media.size is None:
        raise MissingMediaPropertyError(name="size")
    if media.duration is None:
        raise MissingMediaPropertyError(name="duration")
    if media.video is None:
        raise MissingMediaPropertyError(name="video")
    if media.video.width is None:
        raise MissingMediaPropertyError(name="width")
    if media.video.height is None:
        raise MissingMediaPropertyError(name="height")
    if media.video.codec is None:
        raise MissingMediaPropertyError(name="codec")
    if media.video.profile is None:
        raise MissingMediaPropertyError(name="profile")
    if media.video.pix_fmt is None:
        raise MissingMediaPropertyError(name="pix_fmt")
    if media.video.fps is None:
        raise MissingMediaPropertyError(name="fps")
    if media.video.bit_rate is None:
        raise MissingMediaPropertyError(name="bit_rate")
    if media.audio is None:
        raise MissingMediaPropertyError(name="audio")
    if media.subtitles is None:
        raise MissingMediaPropertyError(name="subtitles")

    lines = [
        f"File: {input_single.name}",
        f"Size: {_build_size_display(media.size)} | "
        f"Duration: {_build_duration_display(media.duration)}",
        f"Video: {media.video.width}x{media.video.height}, {media.video.codec}, "
        f"{media.video.pix_fmt}, {media.video.fps} fps, {media.video.bit_rate} kb/s",
    ]

    audio_line = _build_audio_line(tracks=media.audio, max_len=preset.max_line_length)
    if audio_line:
        lines.append(audio_line)

    sub_line = _build_subtitles_line(
        subtitles=media.subtitles, max_len=preset.max_line_length
    )
    if sub_line:
        lines.append(sub_line)

    line_height = preset.fontsize + preset.line_gap
    header_height = preset.header_margin_top + line_height * len(lines)

    filters = [f"pad=iw:ih+{header_height}:0:{header_height}:color={preset.background}"]
    for i, line in enumerate(lines):
        y = preset.header_margin_top + i * line_height
        filters.append(
            f"drawtext=fontfile={preset.fontfile.as_posix()}:"
            f"text='{_escape_drawtext(line)}':"
            f"fontsize={preset.fontsize}:fontcolor={preset.text_color}:"
            f"x={preset.header_margin_left}:y={y}"
        )

    return [
        "ffmpeg",
        "-y",
        "-i",
        str(input_single),
        "-vf",
        ",".join(filters),
        str(params.output),
    ]


# Proceso
# -----------------------------------------------------------------------------


def sheet_cmd(params: SheetParameters) -> list[list[str]]:
    """Composición de llamada ffmpeg para generar una hoja de captura encadenada.

    Args:
        params: Parámetros validados y parseados obtenidos de los argumentos de CLI.

    Returns:
        cmd: comando de ffmpeg listo para consumo.

    Raises:
        CommandGenerationError: Si problema en la generación de comandos.
    """

    tile_tmp = Path("tile_tmp.jpg")

    snapshots_cmd = _generate_snapshots(params=params, output=tile_tmp)

    if snapshots_cmd is None:
        raise CommandGenerationError(command_name="snapshots_cmd")

    header_cmd = _generate_header(params=params, input_single=tile_tmp)

    if header_cmd is None:
        raise CommandGenerationError(command_name="header_cmd")

    return [snapshots_cmd, header_cmd]
