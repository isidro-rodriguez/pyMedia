from pymedia.logger import get_logger
from pymedia.models.errors import ValueComparisonError
from pymedia.models.media import Media
from pymedia.models.state import state
from pymedia.services.pipeline_service import process_crop
from pymedia.utils import parse_crop

logger = get_logger("concat")


def _target_fps() -> str:
    """Calcula el fps objetivo según el modo min/max del config."""
    fps_list: list[str] = []

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
    media_heights: list[int] = []
    for media in state.media:
        media_heights.append(media.video.height)

    match state.config.conflictive_join.resize_to:
        case "min_height":
            return min(media_heights)
        case "max_height":
            return max(media_heights)
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
            and height > state.arguments.scale.value
        )

    # Alturas diferentes → necesitan escalado para normalizar
    return True


def _scaled_dims() -> list[tuple[int, int]]:
    """Calcula las dimensiones post-escalado de cada vídeo."""
    pipeline = state.video_pipeline
    dims: list[tuple[int, int]] = []

    for i, media in enumerate(state.media):
        if pipeline.scale and pipeline.scale[i]:
            scale_value = state.arguments.scale.value
            height = scale_value
            width = round(media.video.width * height / media.video.height / 2) * 2
        else:
            width, height = media.video.width, media.video.height
        dims.append((width, height))

    return dims


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
    return args


def _build_video_chain(index: int, target: dict) -> str:
    """Construye la cadena de filtros de vídeo para una entrada."""
    pipeline = state.video_pipeline
    video_filters: list[str] = []
    video_filter_str = ""

    # Escalado — solo si es necesario
    if target["needs_scale"]:
        if target["needs_normalize"]:
            video_filters.append(f"scale={target['width']}:{target['height']}")
        elif pipeline.scale and pipeline.scale[index]:
            w, h = target["scaled_dims"][index]
            video_filters.append(f"scale={w}:{h}")
        else:
            video_filters.append(f"scale=-2:{target['height']}")

    # Si opción de cortado de imagen
    if pipeline.crop and pipeline.crop[index]:
        video_filters.append(pipeline.crop[index])

    # Si opción giro
    if pipeline.gyrate:
        video_filters.append(pipeline.gyrate)

    if video_filters:
        video_filter_str += ",".join(video_filters) + ","

    # Normalización común — se omiten filtros no necesarios
    normalization = ["setsar=1"]
    if target["needs_fps"]:
        normalization.append(f"fps={target['fps']}")
    if target["needs_pix_fmt"]:
        normalization.append(f"format={target['pix_fmt']}")
    normalization.append("setpts=PTS-STARTPTS")
    normalization_str = ",".join(normalization)

    return f"[{index}:v]{video_filter_str}{normalization_str}[v{index}]"


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


def _recalculate_crop(target: dict) -> None:
    """Recalcula el crop sobre la resolución normalizada para concat."""
    if state.arguments is None or state.arguments.crop is None:
        return

    if parse_crop(state.arguments.crop) is None:
        return

    dimensions: list[tuple[int, int]] = []

    for i in range(len(state.media)):
        if target["needs_normalize"]:
            width, height = target["width"], target["height"]
        else:
            width, height = target["scaled_dims"][i]
        dimensions.append((width, height))

    state.video_pipeline.crop = process_crop(
        state.arguments.crop, state.media, dimensions
    )


def concat_filter_cmd():
    """Construye el comando ffmpeg para unión recodificada con filter_complex."""
    inputs: list[str] = []
    media_filters: list[str] = []
    scaled_dims = _scaled_dims()
    scale_value = state.arguments.scale.value if state.arguments.scale else None
    heights = [m.video.height for m in state.media if m.video is not None]

    if scale_value is not None and scale_value < min(heights):
        target_height = scale_value
    else:
        target_height = _target_height()

    first_media = state.media[0]
    target_width = (
        round(first_media.video.width * target_height / first_media.video.height / 2)
        * 2
    )
    target = {
        "height": target_height,
        "width": target_width,
        "scaled_dims": scaled_dims,
        "fps": _target_fps(),
        "pix_fmt": state.config.conflictive_join.pix_fmt,
        "channel_layout": _channel_layout(),
        "needs_scale": _needs_scale(),
        "needs_normalize": len(set(scaled_dims)) > 1,
        "needs_fps": _needs_fps(),
        "needs_pix_fmt": _needs_pix_fmt(),
        "all_audio_compatible": _all_audio_compatible(),
        "has_audio": any(m.audio is not None for m in state.media),
    }

    _recalculate_crop(target)

    for i in range(len(state.media)):
        inputs.append("-i")
        inputs.append(str(state.inputs[i]))

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
        *inputs,
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
