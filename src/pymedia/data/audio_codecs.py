from dataclasses import dataclass


@dataclass(frozen=True)
class AudioCodecData:
    name: str
    library: str
    containers: tuple[str, ...]
    bit_rates: tuple[str, ...] | None = None


_aac = AudioCodecData(
    name="aac",
    library="aac",
    containers=(".m4a", ".mka", ".mkv", ".mov", ".mp4", ".ts"),
    bit_rates=("96k", "128k", "160k", "192k", "224k", "256k", "320k"),
)

_ac3 = AudioCodecData(
    name="ac3",
    library="ac3",
    containers=(".ac3", ".m2ts", ".mka", ".mkv", ".ts"),
    bit_rates=("192k", "224k", "384k", "448k", "640k"),
)

# Lossless: FFmpeg no requiere ni acepta el flag -b:a
_alac = AudioCodecData(
    name="alac",
    library="alac",
    containers=(".m4a", ".mka", ".mkv", ".mov", ".mp4"),
)

_amr_nb = AudioCodecData(
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
)

_amr_wb = AudioCodecData(
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
)

_eac3 = AudioCodecData(
    name="eac3",
    library="eac3",
    containers=(".m2ts", ".mka", ".mkv", ".mp4", ".ts"),
    bit_rates=("192k", "224k", "256k", "320k", "384k", "448k", "640k"),
)

# Lossless: FFmpeg no requiere ni acepta el flag -b:a
_flac = AudioCodecData(
    name="flac",
    library="flac",
    containers=(".flac", ".mka", ".mkv", ".ogg"),
)

_maven1 = AudioCodecData(
    name="maven1",
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
)

_maven2 = AudioCodecData(
    name="maven2",
    library="mp2",
    containers=(".mp2", ".mkv", ".avi", ".mov"),
    bit_rates=(
        "32k",
        "48k",
        "56k",
        "64k",
        "80k",
        "96k",
        "112k",
        "128k",
        "160k",
        "192k",
        "224k",
        "256k",
        "320k",
        "384k",
    ),
)

# Lossless: FFmpeg no requiere ni acepta el flag -b:a
_mlp = AudioCodecData(
    name="mlp",
    library="mlp",
    containers=(".mlp", ".mka", ".mkv"),
)

_mp2 = AudioCodecData(
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
)

_mp3 = AudioCodecData(
    name="mp3",
    library="libmp3lame",
    containers=(".mp3", ".mka", ".mkv"),
    bit_rates=("96k", "128k", "160k", "192k", "224k", "256k", "320k"),
)

_opus = AudioCodecData(
    name="opus",
    library="libopus",
    containers=(".mka", ".mkv", ".ogg", ".opus", ".webm"),
    bit_rates=("64k", "96k", "128k", "160k", "192k", "256k"),
)

# PCM: FFmpeg calcula el bitrate implícitamente según sample rate, bits y canales
_pcm_s16le = AudioCodecData(
    name="pcm_s16le",
    library="pcm_s16le",
    containers=(".wav", ".avi", ".mkv", ".mov", ".aiff", ".raw"),
)

# PCM: FFmpeg calcula el bitrate implícitamente según sample rate, bits y canales
_pcm_s24le = AudioCodecData(
    name="pcm_s24le",
    library="pcm_s24le",
    containers=(".wav", ".mkv", ".mov", ".aiff", ".raw", ".flac"),
)

# PCM: FFmpeg calcula el bitrate implícitamente según sample rate, bits y canales
_pcm_s32le = AudioCodecData(
    name="pcm_s32le",
    library="pcm_s32le",
    containers=(".wav", ".mkv", ".mov", ".aiff", ".raw"),
)

# PCM: FFmpeg calcula el bitrate implícitamente según sample rate, bits y canales
_pcm_f32le = AudioCodecData(
    name="pcm_f32le",
    library="pcm_f32le",
    containers=(".wav", ".mkv", ".mov", ".aiff", ".raw"),
)

# PCM: FFmpeg calcula el bitrate implícitamente según sample rate, bits y canales
_pcm_alaw = AudioCodecData(
    name="pcm_alaw",
    library="pcm_alaw",
    containers=(".wav", ".au", ".raw", ".mkv", ".mov", ".rtp"),
)

# PCM: FFmpeg calcula el bitrate implícitamente según sample rate, bits y canales
_pcm_mulaw = AudioCodecData(
    name="pcm_mulaw",
    library="pcm_mulaw",
    containers=(".wav", ".au", ".raw", ".mkv", ".mov", ".rtp"),
)

# Lossless: FFmpeg no requiere ni acepta el flag -b:a
_truehd = AudioCodecData(
    name="truehd",
    library="truehd",
    containers=(".mkv", ".mka", ".thd", ".m2ts"),
)

_vorbis = AudioCodecData(
    name="vorbis",
    library="libvorbis",
    containers=(".mka", ".mkv", ".ogg", ".oga", ".webm"),
    bit_rates=("64k", "96k", "128k", "160k", "192k", "256k"),
)


AUDIO_CODECS = {
    "aac": _aac,
    "ac3": _ac3,
    "alac": _alac,
    "amr_nb": _amr_nb,
    "amr_wb": _amr_wb,
    "eac3": _eac3,
    "flac": _flac,
    "maven1": _maven1,
    "maven2": _maven2,
    "mlp": _mlp,
    "mp2": _mp2,
    "mp3": _mp3,
    "opus": _opus,
    "pcm_s16le": _pcm_s16le,
    "pcm_s24le": _pcm_s24le,
    "pcm_s32le": _pcm_s32le,
    "pcm_f32le": _pcm_f32le,
    "pcm_alaw": _pcm_alaw,
    "pcm_mulaw": _pcm_mulaw,
    "truehd": _truehd,
    "vorbis": _vorbis,
}
