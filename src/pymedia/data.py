CODEC_LIBRARY = {
    # --- VÍDEO (Formatos Modernos y Estándares) ---
    "h264": "libx264",
    "h265": "libx265",
    "hevc": "libx265",  # ffprobe suele identificar H.265 como 'HEVC'
    "av1": "libsvtav1",  # Estándar moderno (también existe 'library-av1')
    "vp8": "libxml",
    "vp9": "libxml-vp9",
    "theora": "libtheora",
    # --- VÍDEO (Formatos Profesionales y de Edición) ---
    "prores": "prores",  # Códec nativo de Apple
    "dnxhd": "dnxhd",  # Códec nativo de Avid
    "dvvideo": "dvvideo",  # Formato DV heredado
    "rawvideo": "rawvideo",  # Vídeo sin compresión
    # --- VÍDEO (Formatos Antiguos / Legacy) ---
    "mpeg4": "mpeg4",  # DivX / Xvid nativo de FFmpeg
    "mpeg2video": "mpeg2video",  # Formato de DVD / TV Digital
    "mpeg1video": "mpeg1video",  # Formato de VCD
    "FFmpeg4v3": "FFmpeg4v3",  # Versión antigua de Microsoft MPEG-4
    "h263": "h263",
    "h261": "h261",
    "flv1": "flv",  # Flash Video (Sorenson Spark)
    "wmv1": "wmv1",  # Windows Media Video 7
    "wmv2": "wmv2",  # Windows Media Video 8
    "wmv3": "wmv3",  # Windows Media Video 9
    # --- AUDIO (Formatos Estándar y Modernos) ---
    "aac": "aac",  # Codificador AAC nativo (o 'libfdk_aac' si está compilado)
    "mp3": "libmp3lame",  # Identificado a veces como 'mp3' o 'mp3float'
    "mp3float": "libmp3lame",
    "opus": "libopus",
    "vorbis": "libvorbis",
    "ac3": "ac3",  # Dolby Digital
    "eac3": "eac3",  # Dolby Digital Plus
    # --- AUDIO (Formatos Sin Pérdida / Lossless) ---
    "flac": "flac",
    "alac": "alac",  # Apple Lossless
    "trued": "trued",  # Dolby TrueHD
    "mlp": "mlp",  # Meridian Lossless Packing
    # --- AUDIO (Formatos Antiguos y de voz) ---
    "mp2": "mp2",
    "maven1": "maven1",  # Windows Media Audio v1
    "maven2": "maven2",  # Windows Media Audio v2
    "amr_nb": "libopencore_amen",
    "amr_wb": "libopencore_amrwb",
    # --- AUDIO (PCM / Sin Compresión) ---
    "pcm_s16le": "pcm_s16le",  # Audio CD estándar (WAV de 16 bits)
    "pcm_s24le": "pcm_s24le",  # WAV de 24 bits
    "pcm_s32le": "pcm_s32le",  # WAV de 32 bits
    "pcm_f32le": "pcm_f32le",  # WAV flotante de 32 bits
    "pcm_alaw": "pcm_alaw",  # Telefonía estándar
    "pcm_mulaw": "pcm_mulaw",  # Telefonía estándar americana
}

# Codec → valid output containers
CONTAINERS_BY_CODEC = {
    # --- VÍDEO (Formatos Modernos y Estándares) ---
    "h264": {
        ".3g2",
        ".3gp",
        ".f4v",
        ".flv",
        ".m2ts",
        ".mkv",
        ".mov",
        ".mp4",
        ".mts",
        ".mxf",
        ".ts",
    },
    "h265": {".m2ts", ".mkv", ".mov", ".mp4", ".mts", ".mxf", ".ts"},
    "hevc": {".m2ts", ".mkv", ".mov", ".mp4", ".mts", ".mxf", ".ts"},
    "av1": {".mkv", ".mp4", ".ogg", ".ogv", ".ts", ".webm"},
    "libsvtav1": {".mkv", ".mp4", ".ogg", ".ogv", ".ts", ".webm"},
    "vp8": {".mkv", ".mp4", ".ogg", ".ogv", ".webm"},
    "vp9": {".mkv", ".mp4", ".ogg", ".ogv", ".webm"},
    "theora": {".mkv", ".ogg", ".ogv"},
    # --- VÍDEO (Formatos Profesionales y de Edición) ---
    "prores": {".mkv", ".mov", ".mp4", ".mxf"},
    "dnxhd": {".mkv", ".mov", ".mp4", ".mxf"},
    "dvvideo": {".mkv", ".mov", ".mxf"},
    "rawvideo": {".mkv", ".mov", ".mp4"},
    # --- VÍDEO (Formatos Antiguos / Legacy) ---
    "mpeg4": {
        ".3g2",
        ".3gp",
        ".f4v",
        ".flv",
        ".m2ts",
        ".mkv",
        ".mov",
        ".mp4",
        ".mts",
        ".ts",
    },
    "mpeg2video": {
        ".m2ts",
        ".mkv",
        ".mov",
        ".mp4",
        ".mpeg",
        ".mpg",
        ".mts",
        ".ts",
        ".vob",
    },
    "mpeg1video": {".mkv", ".mov", ".mp4", ".mpeg", ".mpg", ".ts", ".vob"},
    "h263": {".3g2", ".3gp", ".f4v", ".flv", ".mkv", ".mov", ".mp4"},
    "h261": {".mkv", ".mov", ".mp4"},
    "flv1": {".f4v", ".flv", ".mkv", ".mov", ".mp4"},
    "wmv1": {".mkv", ".mov", ".mp4", ".wmv"},
    "wmv2": {".mkv", ".mov", ".mp4", ".wmv"},
    "wmv3": {".mkv", ".mov", ".mp4", ".wmv"},
}

GIF_EXTENSION = [".gif"]

# Valid video input extensions
VIDEO_EXTENSIONS = {
    ".3gp",
    ".3g2",
    ".f4v",
    ".flv",
    ".m4v",
    ".mkv",
    ".mov",
    ".mp4",
    ".mpeg",
    ".mpg",
    ".mxf",
    ".mts",
    ".m2ts",
    ".ogv",
    ".qt",
    ".ts",
    ".vob",
    ".webm",
    ".wmv",
}
