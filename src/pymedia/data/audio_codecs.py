"""Datos estáticos de códecs de audio soportados."""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True)
class AudioCodecData:
    """Representa la configuración e información técnica de un códec de audio.

    Esta clase inmutable almacena los parámetros necesarios para la
    validación, filtrado y construcción de comandos de codificación de audio con FFmpeg.

    Attributes:
        name: Nombre identificador del códec de audio (p. ej., 'aac', 'flac',
            'mp3').
        library: Nombre del codificador/librería utilizado por FFmpeg (p. ej.,
            'aac', 'libmp3lame', 'flac').
        containers: Tupla con las extensiones de contenedor soportadas (p. ej.,
            ('.mp3', '.mkv', '.mp4')).
        bit_rates: Tupla de tasas de bits (bitrates) comunes o recomendadas en
            kbps (p. ej., ('128k', '192k', '320k')). Es None si el códec es sin
            pérdidas (lossless) o no utiliza tasas discretas de bits.
    """

    name: str
    library: str
    containers: tuple[str, ...]
    bit_rates: tuple[str, ...] | None = None


_AUDIO_CODECS: tuple[AudioCodecData, ...] = (
    AudioCodecData(
        name="aac",
        library="aac",
        containers=(".m4a", ".mka", ".mkv", ".mov", ".mp4", ".ts"),
        bit_rates=("96k", "128k", "160k", "192k", "224k", "256k", "320k"),
    ),
    AudioCodecData(
        name="ac3",
        library="ac3",
        containers=(".ac3", ".m2ts", ".mka", ".mkv", ".ts"),
        bit_rates=("192k", "224k", "384k", "448k", "640k"),
    ),
    # Lossless: FFmpeg no requiere ni acepta el flag -b:a
    AudioCodecData(
        name="alac",
        library="alac",
        containers=(".m4a", ".mka", ".mkv", ".mov", ".mp4"),
    ),
    AudioCodecData(
        name="amr_nb",
        library="libopencore_amrnb",
        containers=(".amr", ".3gp"),
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
        bit_rates=("192k", "224k", "256k", "320k", "384k", "448k", "640k"),
    ),
    # Lossless: FFmpeg no requiere ni acepta el flag -b:a
    AudioCodecData(
        name="flac",
        library="flac",
        containers=(".flac", ".mka", ".mkv", ".ogg"),
    ),
    # Lossless: FFmpeg no requiere ni acepta el flag -b:a
    AudioCodecData(
        name="mlp",
        library="mlp",
        containers=(".mlp", ".mka", ".mkv"),
    ),
    AudioCodecData(
        name="mp1",
        library="mp1",
        containers=(".mp1", ".mkv", ".avi", ".mov"),
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
        bit_rates=("96k", "128k", "160k", "192k", "224k", "256k", "320k"),
    ),
    AudioCodecData(
        name="opus",
        library="libopus",
        containers=(".mka", ".mkv", ".mp4", ".ogg", ".opus", ".webm"),
        bit_rates=("64k", "96k", "128k", "160k", "192k", "256k"),
    ),
    # PCM: FFmpeg calcula el bitrate implícitamente según sample rate, bits y canales
    AudioCodecData(
        name="pcm_s16le",
        library="pcm_s16le",
        containers=(".wav", ".avi", ".mkv", ".mov", ".aiff", ".raw"),
    ),
    AudioCodecData(
        name="pcm_s24le",
        library="pcm_s24le",
        containers=(".wav", ".mkv", ".mov", ".aiff", ".raw", ".flac"),
    ),
    AudioCodecData(
        name="pcm_s32le",
        library="pcm_s32le",
        containers=(".wav", ".mkv", ".mov", ".aiff", ".raw"),
    ),
    AudioCodecData(
        name="pcm_f32le",
        library="pcm_f32le",
        containers=(".wav", ".mkv", ".mov", ".aiff", ".raw"),
    ),
    AudioCodecData(
        name="pcm_alaw",
        library="pcm_alaw",
        containers=(".wav", ".au", ".raw", ".mkv", ".mov", ".rtp"),
    ),
    AudioCodecData(
        name="pcm_mulaw",
        library="pcm_mulaw",
        containers=(".wav", ".au", ".raw", ".mkv", ".mov", ".rtp"),
    ),
    # Lossless: FFmpeg no requiere ni acepta el flag -b:a
    AudioCodecData(
        name="truehd",
        library="truehd",
        containers=(".mkv", ".mka", ".thd", ".m2ts"),
    ),
    AudioCodecData(
        name="vorbis",
        library="libvorbis",
        containers=(".mka", ".mkv", ".ogg", ".oga", ".webm"),
        bit_rates=("64k", "96k", "128k", "160k", "192k", "256k"),
    ),
)

AUDIO_CODECS: Mapping[str, AudioCodecData] = MappingProxyType(
    {codec.name: codec for codec in _AUDIO_CODECS}
)