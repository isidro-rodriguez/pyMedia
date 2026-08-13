from dataclasses import dataclass


@dataclass(frozen=True)
class VideoCodecData:
    name: str
    library: str
    containers: list[str]
    crf: tuple[int, int] | None = None
    pix_fmt: list[str] | None = None
    presets: list[str] | None = None


_av1 = VideoCodecData(
    name="av1",
    library="libsvtav1",
    containers=[".mkv", ".mp4", ".ogg", ".ogv", ".ts", ".webm"],
    crf=(0, 63),
    pix_fmt=[
        "yuv420p",
        "yuv420p10le",
        "yuv422p",
        "yuv422p10le",
        "yuv444p",
        "yuv444p10le",
    ],
    presets=[
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "11",
        "12",
        "13",
        "14",
    ],
)

_dnxhd = VideoCodecData(
    name="dnxhd",
    library="dnxhd",
    containers=[".mkv", ".mov", ".mp4", ".mxf"],
)

_dvvideo = VideoCodecData(
    name="dvvideo",
    library="dvvideo",
    containers=[".mkv", ".mov", ".mxf"],
)

_flv1 = VideoCodecData(
    name="flv1",
    library="flv",
    containers=[".f4v", ".flv", ".mkv", ".mov", ".mp4"],
)

_h261 = VideoCodecData(
    name="h261",
    library="h261",
    containers=[".mkv", ".mov", ".mp4"],
)

_h263 = VideoCodecData(
    name="h263",
    library="h263",
    containers=[".3g2", ".3gp", ".f4v", ".flv", ".mkv", ".mov", ".mp4"],
)

_h264 = VideoCodecData(
    name="h264",
    library="libx264",
    containers=[
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
    ],
    crf=(0, 51),
    pix_fmt=[
        "yuv420p",
        "yuv420p10le",
        "yuv422p",
        "yuv422p10le",
        "yuv444p",
        "yuv444p10le",
    ],
    presets=[
        "ultrafast",
        "superfast",
        "veryfast",
        "faster",
        "fast",
        "medium",
        "slow",
        "slower",
        "veryslow",
        "placebo",
    ],
)

_h265 = VideoCodecData(
    name="h265",
    library="libx265",
    containers=[
        ".m2ts",
        ".mkv",
        ".mov",
        ".mp4",
        ".mts",
        ".mxf",
        ".ts",
    ],
    crf=(0, 51),
    pix_fmt=[
        "yuv420p",
        "yuv420p10le",
        "yuv422p",
        "yuv422p10le",
        "yuv444p",
        "yuv444p10le",
    ],
    presets=[
        "ultrafast",
        "superfast",
        "veryfast",
        "faster",
        "fast",
        "medium",
        "slow",
        "slower",
        "veryslow",
        "placebo",
    ],
)

_mpeg1video = VideoCodecData(
    name="mpeg1video",
    library="mpeg1video",
    containers=[".mkv", ".mov", ".mp4", ".mpeg", ".mpg", ".ts", ".vob"],
)

_mpeg2video = VideoCodecData(
    name="mpeg2video",
    library="mpeg2video",
    containers=[
        ".m2ts",
        ".mkv",
        ".mov",
        ".mp4",
        ".mpeg",
        ".mpg",
        ".mts",
        ".ts",
        ".vob",
    ],
)

_mpeg4 = VideoCodecData(
    name="mpeg4",
    library="mpeg4",
    containers=[
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
    ],
)

_msmpeg4v3 = VideoCodecData(
    name="msmpeg4v3",
    library="msmpeg4v3",
    containers=[".avi", ".asf", ".wmv"],
)

_prores = VideoCodecData(
    name="prores",
    library="prores",
    containers=[".mkv", ".mov", ".mp4", ".mxf"],
)

_rawvideo = VideoCodecData(
    name="rawvideo",
    library="rawvideo",
    containers=[".mkv", ".mov", ".mp4"],
)

_theora = VideoCodecData(
    name="theora",
    library="libtheora",
    containers=[".mkv", ".ogg", ".ogv"],
)

_vp8 = VideoCodecData(
    name="vp8",
    library="libvpx",
    containers=[".mkv", ".mp4", ".ogg", ".ogv", ".webm"],
)

_vp9 = VideoCodecData(
    name="vp9",
    library="libvpx-vp9",
    containers=[".mkv", ".mp4", ".ogg", ".ogv", ".webm"],
)

_wmv1 = VideoCodecData(
    name="wmv1",
    library="wmv1",
    containers=[".mkv", ".mov", ".mp4", ".wmv"],
)

_wmv2 = VideoCodecData(
    name="wmv2",
    library="wmv2",
    containers=[".mkv", ".mov", ".mp4", ".wmv"],
)

_wmv3 = VideoCodecData(
    name="wmv3",
    library="wmv3",
    containers=[".mkv", ".mov", ".mp4", ".wmv"],
)


VIDEO_CODECS = {
    "av1": _av1,
    "dnxhd": _dnxhd,
    "dvvideo": _dvvideo,
    "flv1": _flv1,
    "h261": _h261,
    "h263": _h263,
    "h264": _h264,
    "h265": _h265,
    "hevc": _h265,
    "mpeg1video": _mpeg1video,
    "mpeg2video": _mpeg2video,
    "mpeg4": _mpeg4,
    "msmpeg4v3": _msmpeg4v3,
    "prores": _prores,
    "rawvideo": _rawvideo,
    "theora": _theora,
    "vp8": _vp8,
    "vp9": _vp9,
    "wmv1": _wmv1,
    "wmv2": _wmv2,
    "wmv3": _wmv3,
}
