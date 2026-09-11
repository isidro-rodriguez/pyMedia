"""Datos estáticos de códecs de audio.

``containers`` contiene los contenedores en los que FFmpeg puede codificar
cada códec.

``remux_containers`` contiene únicamente los contenedores considerados seguros
para remux sin recodificación, usando ``-c copy``.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True)
class AudioCodecData:
    """Representa la configuración e información técnica de un códec de audio.

    Attributes:
        name: Nombre identificador del códec de audio.
        library: Nombre del codificador o librería utilizado por FFmpeg.
        containers: Contenedores soportados para codificación.
        remux_containers: Contenedores seguros para remux con ``-c copy``.
        bit_rates: Tasas de bits comunes o recomendadas en kbps. Es ``None``
            para códecs sin pérdidas o que no utilizan tasas discretas.
    """

    name: str
    library: str
    containers: tuple[str, ...]
    remux_containers: tuple[str, ...]
    bit_rates: tuple[str, ...] | None = None


_AUDIO_CODECS: tuple[AudioCodecData, ...] = (
    AudioCodecData(
        name="aac",
        library="aac",
        containers=(".m4a", ".mka", ".mkv", ".mov", ".mp4", ".ts"),
        remux_containers=(".m4a", ".mka", ".mkv", ".mov", ".mp4", ".ts"),
        bit_rates=("96k", "128k", "160k", "192k", "224k", "256k", "320k"),
    ),
    AudioCodecData(
        name="ac3",
        library="ac3",
        containers=(".ac3", ".m2ts", ".mka", ".mkv", ".ts"),
        remux_containers=(".ac3", ".m2ts", ".mka", ".mkv", ".ts"),
        bit_rates=("192k", "224k", "384k", "448k", "640k"),
    ),
    AudioCodecData(
        name="adpcm_ms",
        library="adpcm_ms",
        containers=(".avi", ".wav", ".asf", ".mkv"),
        remux_containers=(".avi", ".wav", ".asf", ".mkv"),
    ),
    # Lossless: FFmpeg no requiere ni acepta el flag -b:a.
    AudioCodecData(
        name="alac",
        library="alac",
        containers=(".m4a", ".mka", ".mkv", ".mov", ".mp4"),
        remux_containers=(".m4a", ".mka", ".mkv", ".mov", ".mp4"),
    ),
    AudioCodecData(
        name="amr_nb",
        library="libopencore_amrnb",
        containers=(".amr", ".3gp"),
        remux_containers=(".amr", ".3gp"),
        bit_rates=(
            "4.75k",
            "5.15k",
            "5.9k",
            "6.7k",
            "7.4k",
            "7.95k",
            "10.2k",
            "12.2k",
        ),
    ),
    AudioCodecData(
        name="amr_wb",
        library="libvo_amrwbenc",
        containers=(".awb", ".3gp"),
        remux_containers=(".awb", ".3gp"),
        bit_rates=(
            "6.6k",
            "8.85k",
            "12.65k",
            "14.25k",
            "15.85k",
            "18.25k",
            "19.85k",
            "23.05k",
            "23.85k",
        ),
    ),
    AudioCodecData(
        name="eac3",
        library="eac3",
        containers=(".m2ts", ".mka", ".mkv", ".mp4", ".ts"),
        remux_containers=(".m2ts", ".mka", ".mkv", ".mp4", ".ts"),
        bit_rates=("192k", "224k", "256k", "320k", "384k", "448k", "640k"),
    ),
    # Lossless: FFmpeg no requiere ni acepta el flag -b:a.
    AudioCodecData(
        name="flac",
        library="flac",
        containers=(".flac", ".mka", ".mkv", ".ogg"),
        remux_containers=(".flac", ".mka", ".mkv", ".ogg"),
    ),
    # Lossless: FFmpeg no requiere ni acepta el flag -b:a.
    AudioCodecData(
        name="mlp",
        library="mlp",
        containers=(".mlp", ".mka", ".mkv"),
        remux_containers=(".mlp", ".mka", ".mkv"),
    ),
    AudioCodecData(
        name="mp1",
        library="mp1",
        containers=(".mp1", ".mkv", ".avi", ".mov"),
        remux_containers=(".mp1", ".mkv", ".avi"),
        bit_rates=(
            "32k",
            "64k",
            "96k",
            "128k",
            "192k",
            "256k",
            "320k",
            "384k",
            "448k",
        ),
    ),
    AudioCodecData(
        name="mp2",
        library="mp2",
        containers=(".mp2", ".mkv", ".avi", ".mpg", ".mpeg", ".ts", ".vob"),
        remux_containers=(".mp2", ".mkv", ".avi", ".mpg", ".mpeg", ".ts", ".vob"),
        bit_rates=(
            "64k",
            "96k",
            "128k",
            "160k",
            "192k",
            "224k",
            "256k",
            "320k",
            "384k",
        ),
    ),
    AudioCodecData(
        name="mp3",
        library="libmp3lame",
        containers=(".mp3", ".mka", ".mkv"),
        remux_containers=(".mp3", ".mka", ".mkv"),
        bit_rates=("96k", "128k", "160k", "192k", "224k", "256k", "320k"),
    ),
    AudioCodecData(
        name="opus",
        library="libopus",
        containers=(".mka", ".mkv", ".mp4", ".ogg", ".opus", ".webm"),
        # Opus en MP4 depende de la versión de FFmpeg y del reproductor.
        remux_containers=(".mka", ".mkv", ".ogg", ".opus", ".webm"),
        bit_rates=("64k", "96k", "128k", "160k", "192k", "256k"),
    ),
    # PCM: FFmpeg calcula el bitrate según sample rate, bits y canales.
    AudioCodecData(
        name="pcm_s16le",
        library="pcm_s16le",
        containers=(".wav", ".avi", ".mkv", ".mov", ".aiff", ".raw"),
        remux_containers=(".wav", ".avi", ".mkv", ".mov", ".aiff", ".raw"),
    ),
    AudioCodecData(
        name="pcm_s24le",
        library="pcm_s24le",
        containers=(".wav", ".mkv", ".mov", ".aiff", ".raw", ".flac"),
        remux_containers=(".wav", ".mkv", ".mov", ".aiff", ".raw"),
    ),
    AudioCodecData(
        name="pcm_s32le",
        library="pcm_s32le",
        containers=(".wav", ".mkv", ".mov", ".aiff", ".raw"),
        remux_containers=(".wav", ".mkv", ".mov", ".aiff", ".raw"),
    ),
    AudioCodecData(
        name="pcm_f32le",
        library="pcm_f32le",
        containers=(".wav", ".mkv", ".mov", ".aiff", ".raw"),
        remux_containers=(".wav", ".mkv", ".mov", ".aiff", ".raw"),
    ),
    AudioCodecData(
        name="pcm_alaw",
        library="pcm_alaw",
        containers=(".wav", ".au", ".raw", ".mkv", ".mov", ".rtp"),
        remux_containers=(".wav", ".au", ".raw", ".mkv", ".mov", ".rtp"),
    ),
    AudioCodecData(
        name="pcm_mulaw",
        library="pcm_mulaw",
        containers=(".wav", ".au", ".raw", ".mkv", ".mov", ".rtp"),
        remux_containers=(".wav", ".au", ".raw", ".mkv", ".mov", ".rtp"),
    ),
    # Lossless: FFmpeg no requiere ni acepta el flag -b:a.
    AudioCodecData(
        name="truehd",
        library="truehd",
        containers=(".mkv", ".mka", ".thd", ".m2ts"),
        remux_containers=(".mkv", ".mka", ".thd", ".m2ts"),
    ),
    AudioCodecData(
        name="vorbis",
        library="libvorbis",
        containers=(".mka", ".mkv", ".ogg", ".oga", ".webm"),
        remux_containers=(".mka", ".mkv", ".ogg", ".oga", ".webm"),
        bit_rates=("64k", "96k", "128k", "160k", "192k", "256k"),
    ),
)


AUDIO_CODECS: Mapping[str, AudioCodecData] = MappingProxyType(
    {codec.name: codec for codec in _AUDIO_CODECS}
)
"""Códecs de audio soportados indexados por nombre."""
