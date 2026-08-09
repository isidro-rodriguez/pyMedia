from fractions import Fraction

from pymedia.models.errors import ValueComparisonError
from pymedia.models.media import Media
from pymedia.models.state import state


def _target_fps() -> str:
    """Calcula el fps objetivo según el modo min/max del config."""

    fps_list: list[Fraction] = state.media.fps
    for m in state.media:
        fps = m.video.fps
        if fps not in fps_list:
            fps_list.append(fps)

    match state.config.conflictive_join.fps:
        case "min_fps":
            return str(min(fps_list))
        case "max_fps":
            return str(max(fps_list))
        case _:
            return "30"


def _channel_layout() -> str:
    """Devuelve el channel_layout según el modo del config."""
    return "stereo" if state.config.conflictive_join.channels == "stereo" else "mono"


def _target_height() -> int:
    """Calcula la altura objetivo según el modo min/max del config."""
    match state.config.conflictive_join.resize_to:
        case "min_height":
            return min(x for x in state.media.height)
        case "max_height":
            return max(x for x in state.media.height)
        case _:
            raise ValueComparisonError("concat", "Height")


def _needs_scale() -> bool:
    """True si hay que escalar: alturas distintas o escala explícita del usuario."""
    heights = {m.video.height for m in state.media if m.video is not None}

    all_same = len(heights) <= 1

    if all_same:
        # Solo escalar si el usuario pidió una resolución menor
        height = next(iter(heights))
        return (
            state.video_pipeline.scale is not None
            and height > state.video_pipeline.scale[0]
        )

    # Alturas diferentes → necesitan escalado para normalizar
    return True


def _needs_fps() -> bool:
    """True si los vídeos tienen fps distintos (o desconocido)."""
    return len({m.video.fps for m in state.media if m.video is not None}) > 1


def _needs_pix_fmt() -> bool:
    """True si los vídeos tienen pix_fmt distintos (o desconocido)."""
    return len({m.video.pix_fmt for m in state.media if m.video is not None}) > 1


def _all_audio_compatible() -> bool:
    """True si todos tienen audio y son idénticos en codec/rate/channels/layout."""
    if any(m.audio is None for m in state.media):
        return False
    signatures = {
        (m.audio.codec, m.audio.sample_rate, m.audio.channels, m.audio.channel_layout)
        for m in state.media
    }
    return len(signatures) == 1


def _build_input_args() -> list[str]:
    """Construye los argumentos -i de ffmpeg para todas las entradas."""
    args: list[str] = []
    for i in range(len(state.media)):
        args.append("-i")
        args.append(str(state.inputs[i]))
    return args


def _build_video_chain(index: int, target: dict) -> str:
    """Construye la cadena de filtros de vídeo para una entrada."""
    pipeline = state.video_pipeline
    video_filters: list[str] = []

    # Si opción de cortado de imagen
    if pipeline.crop:
        video_filters.append(pipeline.crop)

    # Si opción giro
    if pipeline.gyrate:
        video_filters.append(pipeline.gyrate)

    # Escalado — solo si es necesario
    if target["needs_scale"]:
        if pipeline.scale:
            video_filters.append(pipeline.scale)
        else:
            video_filters.append(f"scale=-2:{target['height']}")

    video_filter_str = ",".join(video_filters)
    if video_filter_str:
        video_filter_str += ","

    # Normalización común — se omiten filtros no necesarios
    normalization = ["setsar=1"]
    if target["needs_fps"]:
        normalization.append(f"fps={target['fps']}")
    if target["needs_pix_fmt"]:
        normalization.append(f"format={target['pix_fmt']}")
    normalization.append("setpts=PTS-STARTPTS")

    return f"[{index}:v]{video_filter_str}{','.join(normalization)}[v{index}]"


def _build_audio_chain(media: Media, index: int, target: dict) -> str:
    """Construye la cadena de filtros de audio para una entrada."""
    if media.audio is None:
        raise ValueError("Stream de audio no encontrado en unión recodificada")

    if target["all_audio_compatible"]:
        # Todos los audios son idénticos — solo resetear timestamps
        return f"[{index}:a]asetpts=PTS-STARTPTS[a{index}]"

    # Audios incompatibles → normalizar
    # noinspection SpellCheckingInspection
    return (
        f"[{index}:a]aresample=48000,"
        f"aformat=sample_fmts=fltp:channel_layouts={target['channel_layout']},"
        f"asetpts=PTS-STARTPTS[a{index}]"
    )


def _build_concat_graph(n: int, has_audio: bool = True) -> str:
    """Construye el grafo concat final con en entradas."""
    if has_audio:
        labels = "".join(f"[v{i}][a{i}]" for i in range(n))
        return f"{labels}concat=n={n}:v=1:a=1[v][a]"
    labels = "".join(f"[v{i}]" for i in range(n))
    return f"{labels}concat=n={n}:v=1:a=0[v]"


def _determine_targets() -> dict:
    """Determina los targets y qué normalización es realmente necesaria."""
    conflict = state.config.conflictive_join
    return {
        "height": _target_height(),
        "fps": _target_fps(),
        "pix_fmt": conflict.pix_fmt,
        "channel_layout": _channel_layout(),
        "needs_scale": _needs_scale(),
        "needs_fps": _needs_fps(),
        "needs_pix_fmt": _needs_pix_fmt(),
        "all_audio_compatible": _all_audio_compatible(),
        "has_audio": any(m.audio is not None for m in state.media),
    }


def concat_filter_cmd():
    """Construye el comando ffmpeg para unión recodificada con filter_complex."""
    target = _determine_targets()

    input_args = _build_input_args()

    media_filters: list[str] = []
    for i, media in enumerate(state.media):
        media_filters.append(_build_video_chain(i, target))
        if target["has_audio"]:
            media_filters.append(_build_audio_chain(media, i, target))

    filters = (
        ";".join(media_filters)
        + ";"
        + _build_concat_graph(len(state.media), target["has_audio"])
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-nostdin",
        "-loglevel",
        "error",
        *input_args,
        "-filter_complex",
        filters,
        "-map",
        "[v]",
        "-c:v",
        state.config.encode.video_codec,
        "-preset",
        state.config.encode.video_preset,
        "-crf",
        str(state.config.encode.video_crf),
        "-threads",
        "1",
    ]
    if target["has_audio"]:
        cmd.extend(["-map", "[a]", "-c:a", state.config.encode.audio_codec])
    cmd.append(state.output)

    return cmd
