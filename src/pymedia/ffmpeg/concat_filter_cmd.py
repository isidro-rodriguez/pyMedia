from dataclasses import dataclass

from pymedia.logger import get_logger
from pymedia.models.errors import ValueComparisonError
from pymedia.models.media import Media
from pymedia.models.state import state
from pymedia.services.pipeline_service import process_crop
from pymedia.utils import parse_crop

logger = get_logger("concat")


@dataclass
class TargetRequirements:
    """Valores objetivo derivados de media + config + pipeline."""

    height: int
    width: int
    fps: str
    pix_fmt: str
    channel_layout: str
    has_audio: bool


@dataclass
class TargetDerived:
    """Valores calculados a partir de los requirements."""

    scaled_dims: list[tuple[int, int]]
    needs_scale: bool
    needs_normalize: bool
    needs_fps: bool
    needs_pix_fmt: bool
    all_audio_compatible: bool


@dataclass
class TargetFinal:
    """Valores listos para el comando ffmpeg."""

    inputs: list[str]
    filters: str
    has_audio: bool


# -----------------------------------------------------------------------------
#  Cálculo de valores objetivo
# -----------------------------------------------------------------------------


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


def _build_requirements() -> TargetRequirements:
    """Construye los valores objetivo a partir de media, config y pipeline."""
    heights = [m.video.height for m in state.media if m.video is not None]
    min_height = min(heights)

    # Altura objetivo: si el usuario pide un scale menor que la altura mínima,
    # se usa ese valor; si no, se usa la altura del config (min/max).
    scale_value: int | None = None
    if state.arguments is not None and state.arguments.scale is not None:
        scale_value = state.arguments.scale.value

    if scale_value is not None and scale_value < min_height:
        target_height = scale_value
    else:
        target_height = _target_height()

    # Ancho objetivo: proporcional al primer vídeo, redondeado a par
    first_media = state.media[0]
    first_width = first_media.video.width or 0
    first_height = first_media.video.height or 1
    target_width = round(first_width * target_height / first_height / 2) * 2

    return TargetRequirements(
        height=target_height,
        width=target_width,
        fps=_target_fps(),
        pix_fmt=state.config.conflictive_join.pix_fmt,
        channel_layout=_channel_layout(),
        has_audio=any(m.audio is not None for m in state.media),
    )


# -----------------------------------------------------------------------------
#  Cálculo de valores derivados
# -----------------------------------------------------------------------------


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


def _recalculate_crop(req: TargetRequirements, derived: TargetDerived) -> None:
    """Recalcula el crop sobre la resolución post-escalado para concat."""
    if state.arguments is None or state.arguments.crop is None:
        return

    if parse_crop(state.arguments.crop) is None:
        return

    dimensions: list[tuple[int, int]] = []

    for i in range(len(state.media)):
        if derived.needs_normalize:
            width, height = req.width, req.height
        else:
            width, height = derived.scaled_dims[i]
        dimensions.append((width, height))

    state.video_pipeline.crop = process_crop(
        state.arguments.crop, state.media, dimensions
    )


def _build_derived(req: TargetRequirements) -> TargetDerived:
    """Construye los valores calculados a partir de los requirements."""
    scaled_dims = _scaled_dims()

    derived = TargetDerived(
        scaled_dims=scaled_dims,
        needs_scale=_needs_scale(),
        needs_normalize=len(set(scaled_dims)) > 1,
        needs_fps=_needs_fps(),
        needs_pix_fmt=_needs_pix_fmt(),
        all_audio_compatible=_all_audio_compatible(),
    )

    # El crop debe recalcularse sobre la resolución post-escalado
    _recalculate_crop(req, derived)

    return derived


# -----------------------------------------------------------------------------
#  Ensamblado de filtros y comando ffmpeg
# -----------------------------------------------------------------------------


def _build_video_chain(
    index: int, req: TargetRequirements, derived: TargetDerived
) -> str:
    """Construye la cadena de filtros de vídeo para una entrada."""
    pipeline = state.video_pipeline
    video_filters: list[str] = []
    video_filter_str = ""

    # Escalado — solo si es necesario
    if derived.needs_scale:
        if derived.needs_normalize:
            video_filters.append(f"scale={req.width}:{req.height}")
        elif pipeline.scale and pipeline.scale[index]:
            w, h = derived.scaled_dims[index]
            video_filters.append(f"scale={w}:{h}")
        else:
            video_filters.append(f"scale=-2:{req.height}")

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
    if derived.needs_fps:
        normalization.append(f"fps={req.fps}")
    if derived.needs_pix_fmt:
        normalization.append(f"format={req.pix_fmt}")
    normalization.append("setpts=PTS-STARTPTS")
    normalization_str = ",".join(normalization)

    return f"[{index}:v]{video_filter_str}{normalization_str}[v{index}]"


def _build_audio_chain(
    media: Media, index: int, req: TargetRequirements, derived: TargetDerived
) -> str:
    """Construye la cadena de filtros de audio para una entrada."""
    if media.audio is None:
        raise ValueError("Stream de audio no encontrado en unión recodificada")

    if derived.all_audio_compatible:
        # Todos los audios son idénticos — solo resetear timestamps
        return f"[{index}:a]asetpts=PTS-STARTPTS[a{index}]"

    # Audios incompatibles → normalizar
    # noinspection SpellCheckingInspection
    return (
        f"[{index}:a]aresample=48000,"
        f"aformat=sample_fmts=fltp:channel_layouts={req.channel_layout},"
        f"asetpts=PTS-STARTPTS[a{index}]"
    )


def _build_concat_graph(n: int, has_audio: bool = True) -> str:
    """Construye el grafo concat final con en entradas."""
    if has_audio:
        labels = "".join(f"[v{i}][a{i}]" for i in range(n))
        return f"{labels}concat=n={n}:v=1:a=1[v][a]"
    labels = "".join(f"[v{i}]" for i in range(n))
    return f"{labels}concat=n={n}:v=1:a=0[v]"


def _build_final(req: TargetRequirements, derived: TargetDerived) -> TargetFinal:
    """Ensambla los inputs y el grafo de filtros listos para ffmpeg."""
    # Argumentos -i para todas las entradas
    inputs: list[str] = []
    for i in range(len(state.media)):
        inputs.append("-i")
        inputs.append(str(state.inputs[i]))

    # Cadenas de filtros de vídeo y audio por entrada
    media_filters: list[str] = []
    for i, media in enumerate(state.media):
        media_filters.append(_build_video_chain(i, req, derived))
        if req.has_audio:
            media_filters.append(_build_audio_chain(media, i, req, derived))

    # Grafo concat final
    filters = (
        ";".join(media_filters)
        + ";"
        + _build_concat_graph(len(state.media), req.has_audio)
    )

    return TargetFinal(inputs=inputs, filters=filters, has_audio=req.has_audio)


# -----------------------------------------------------------------------------
#  Ensamblado de comando ffmpeg
# -----------------------------------------------------------------------------


def _build_cmd(final: TargetFinal) -> list[str]:
    """Construye el comando ffmpeg completo."""
    cmd = [
        "ffmpeg",
        "-y",
        "-nostdin",
        "-loglevel",
        "error",
        *final.inputs,
        "-filter_complex",
        final.filters,
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
    if final.has_audio:
        cmd.extend(["-map", "[a]", "-c:a", state.config.encode.audio_codec])
    cmd.append(state.output)

    return cmd


# -----------------------------------------------------------------------------
#  Proceso de ejecución
# -----------------------------------------------------------------------------


def concat_filter_cmd():
    """Construye el comando ffmpeg para unión recodificada con filter_complex."""
    req = _build_requirements()
    derived = _build_derived(req)
    final = _build_final(req, derived)
    return _build_cmd(final)
