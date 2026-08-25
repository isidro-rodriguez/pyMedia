from dataclasses import dataclass


@dataclass(frozen=True)
class VideoCodecData:
    name: str
    library: str
    containers: tuple[str, ...]
    crf: tuple[int, int] | None = None
    pix_fmt: str | None = None
    presets: tuple[str, ...] | None = None


VIDEO_CODECS = {
    "av1": VideoCodecData(
        name="av1",
        library="libsvtav1",
        containers=(".mkv", ".mp4", ".ogg", ".ogv", ".ts", ".webm"),
        crf=(0, 63),
        pix_fmt="yuv420p10le",
        presets=(
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
        ),
    ),
    "dnxhd": VideoCodecData(
        name="dnxhd",
        library="dnxhd",
        containers=(".mkv", ".mov", ".mp4", ".mxf"),
    ),
    "dvvideo": VideoCodecData(
        name="dvvideo",
        library="dvvideo",
        containers=(".mkv", ".mov", ".mxf"),
    ),
    "ffv1": VideoCodecData(
        name="ffv1",
        library="ffv1",
        containers=(".avi", ".mkv", ".mov"),
    ),
    "flv1": VideoCodecData(
        name="flv1",
        library="flv",
        containers=(".f4v", ".flv", ".mkv", ".mov", ".mp4"),
    ),
    "h261": VideoCodecData(
        name="h261",
        library="h261",
        containers=(".mkv", ".mov", ".mp4"),
    ),
    "h263": VideoCodecData(
        name="h263",
        library="h263",
        containers=(".3g2", ".3gp", ".f4v", ".flv", ".mkv", ".mov", ".mp4"),
    ),
    "h264": VideoCodecData(
        name="h264",
        library="libx264",
        containers=(
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
        ),
        crf=(0, 51),
        pix_fmt="yuv420p",
        presets=(
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
        ),
    ),
    "h265": VideoCodecData(
        name="h265",
        library="libx265",
        containers=(
            ".m2ts",
            ".mkv",
            ".mov",
            ".mp4",
            ".mts",
            ".mxf",
            ".ts",
        ),
        crf=(0, 51),
        pix_fmt="yuv420p10le",
        presets=(
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
        ),
    ),
    "huffyuv": VideoCodecData(
        name="huffyuv",
        library="huffyuv",
        containers=(".avi", ".mkv", ".mov"),
    ),
    "jpeg2000": VideoCodecData(
        name="jpeg2000",
        library="jpeg2000",
        containers=(".avi", ".mkv", ".mov", ".mp4"),
    ),
    "mjpeg": VideoCodecData(
        name="mjpeg",
        library="mjpeg",
        containers=(".avi", ".mkv", ".mov", ".mp4", ".ts"),
    ),
    "mpeg1video": VideoCodecData(
        name="mpeg1video",
        library="mpeg1video",
        containers=(".mkv", ".mov", ".mp4", ".mpeg", ".mpg", ".ts", ".vob"),
    ),
    "mpeg2video": VideoCodecData(
        name="mpeg2video",
        library="mpeg2video",
        containers=(
            ".m2ts",
            ".mkv",
            ".mov",
            ".mp4",
            ".mpeg",
            ".mpg",
            ".mts",
            ".ts",
            ".vob",
        ),
    ),
    "mpeg4": VideoCodecData(
        name="mpeg4",
        library="mpeg4",
        containers=(
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
        ),
    ),
    "msmpeg4v3": VideoCodecData(
        name="msmpeg4v3",
        library="msmpeg4v3",
        containers=(".avi", ".asf", ".wmv"),
    ),
    "prores": VideoCodecData(
        name="prores",
        library="prores",
        containers=(".mkv", ".mov", ".mp4", ".mxf"),
    ),
    "rawvideo": VideoCodecData(
        name="rawvideo",
        library="rawvideo",
        containers=(".mkv", ".mov", ".mp4"),
    ),
    "rv40": VideoCodecData(
        name="rv40",
        library="rv40",
        containers=(".mkv", ".rm", ".rmvb"),
    ),
    "snow": VideoCodecData(
        name="snow",
        library="snow",
        containers=(".mkv",),
    ),
    "svq3": VideoCodecData(
        name="svq3",
        library="svq3",
        containers=(".mkv", ".mov"),
    ),
    "theora": VideoCodecData(
        name="theora",
        library="libtheora",
        containers=(".mkv", ".ogg", ".ogv"),
    ),
    "utvideo": VideoCodecData(
        name="utvideo",
        library="utvideo",
        containers=(".avi", ".mkv"),
    ),
    "vc1": VideoCodecData(
        name="vc1",
        library="vc1",
        containers=(".asf", ".avi", ".m2ts", ".mkv", ".mov", ".mp4", ".ts", ".wmv"),
    ),
    "vp6": VideoCodecData(
        name="vp6",
        library="vp6",
        containers=(".f4v", ".flv", ".mkv"),
    ),
    "vp8": VideoCodecData(
        name="vp8",
        library="libvpx",
        containers=(".mkv", ".mp4", ".ogg", ".ogv", ".webm"),
    ),
    "vp9": VideoCodecData(
        name="vp9",
        library="libvpx-vp9",
        containers=(".mkv", ".mp4", ".ogg", ".ogv", ".webm"),
    ),
    "wmv1": VideoCodecData(
        name="wmv1",
        library="wmv1",
        containers=(".mkv", ".mov", ".mp4", ".wmv"),
    ),
    "wmv2": VideoCodecData(
        name="wmv2",
        library="wmv2",
        containers=(".mkv", ".mov", ".mp4", ".wmv"),
    ),
    "wmv3": VideoCodecData(
        name="wmv3",
        library="wmv3",
        containers=(".mkv", ".mov", ".mp4", ".wmv"),
    ),
}
