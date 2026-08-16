"""Tests para el servicio de pipeline (pymedia.services.pipeline_service)."""

from datetime import timedelta
from pathlib import Path

import pytest

from pymedia.cli_params import GyrateMode, ScaleGifMode, ScaleVideoMode
from pymedia.errors import (
    CropAllZeroError,
    CropExceedsHeightError,
    CropExceedsWidthError,
    InvalidCropFormatError,
    InvalidGyrateError,
    InvalidTimeFormatError,
    InvalidTrimPointsError,
    MissingMediaError,
    MissingMediaPropertyError,
    NegativeTimeError,
    TimeExceedsDurationError,
)
from pymedia.services.pipeline_service import (
    process_crop,
    process_gyrate,
    process_scale,
    process_time,
    process_trim_points,
)
from utils.factories import make_media, make_video

# -----------------------------------------------------------------------------
#  process_crop()
# -----------------------------------------------------------------------------


class TestProcessCrop:
    def test_valid_crop_single_media(self):
        media = [make_media(video=make_video(width=1920, height=1080))]

        result = process_crop("200,200,0,0", media)

        assert result == ["crop=1520:1080:200:0"]

    def test_valid_crop_multiple_media(self):
        media = [
            make_media(video=make_video(width=1920, height=1080)),
            make_media(video=make_video(width=1280, height=720)),
        ]

        result = process_crop("100,100,50,50", media)

        assert result == [
            "crop=1720:980:100:50",
            "crop=1080:620:100:50",
        ]

    def test_crop_none_raises(self):
        media = [make_media(video=make_video())]

        with pytest.raises(InvalidCropFormatError):
            process_crop(None, media)

    def test_crop_invalid_format_raises(self):
        media = [make_media(video=make_video())]

        with pytest.raises(InvalidCropFormatError):
            process_crop("1,2,3", media)

    def test_crop_all_zero_raises(self):
        media = [make_media(video=make_video())]

        with pytest.raises(CropAllZeroError):
            process_crop("0,0,0,0", media)

    def test_crop_exceeds_width_raises(self):
        media = [make_media(video=make_video(width=100, height=100))]

        with pytest.raises(CropExceedsWidthError):
            process_crop("60,60,0,0", media)

    def test_crop_exceeds_height_raises(self):
        media = [make_media(video=make_video(width=100, height=100))]

        with pytest.raises(CropExceedsHeightError):
            process_crop("0,0,60,60", media)

    def test_crop_missing_video_raises(self):
        media = [make_media(video=None)]

        with pytest.raises(MissingMediaPropertyError):
            process_crop("10,10,10,10", media)

    def test_crop_missing_dimensions_raises(self):
        media = [make_media(video=make_video(width=None, height=None))]

        with pytest.raises(MissingMediaPropertyError):
            process_crop("10,10,10,10", media)

    def test_crop_with_explicit_dimensions(self):
        media = [make_media(video=make_video(width=1920, height=1080))]

        result = process_crop("100,100,0,0", media, dimensions=[(640, 360)])

        assert result == ["crop=440:360:100:0"]

    def test_crop_with_explicit_dimensions_multiple(self):
        media = [
            make_media(video=make_video(width=1920, height=1080)),
            make_media(video=make_video(width=1280, height=720)),
        ]

        result = process_crop(
            "100,100,50,50", media, dimensions=[(640, 360), (320, 180)]
        )

        assert result == [
            "crop=440:260:100:50",
            "crop=120:80:100:50",
        ]

    def test_crop_exceeds_explicit_dimensions_raises(self):
        media = [make_media(video=make_video(width=1920, height=1080))]

        with pytest.raises(CropExceedsWidthError):
            process_crop("100,100,0,0", media, dimensions=[(150, 100)])

    def test_crop_exceeds_explicit_height_raises(self):
        media = [make_media(video=make_video(width=1920, height=1080))]

        with pytest.raises(CropExceedsHeightError):
            process_crop("0,0,100,80", media, dimensions=[(640, 150)])


# -----------------------------------------------------------------------------
#  process_gyrate()
# -----------------------------------------------------------------------------


class TestProcessGyrate:
    @pytest.mark.parametrize(
        ("mode", "expected"),
        [
            (GyrateMode.d90, "transpose=1"),
            (GyrateMode.d180, "vflip,hflip"),
            (GyrateMode.d270, "transpose=2"),
        ],
    )
    def test_valid_gyrate(self, mode, expected):
        assert process_gyrate(mode) == expected

    def test_invalid_gyrate_raises(self):
        with pytest.raises(InvalidGyrateError):
            process_gyrate("45")  # type: ignore[arg-type]


# -----------------------------------------------------------------------------
#  process_scale()
# -----------------------------------------------------------------------------


class TestProcessScale:
    def test_scale_down(self):
        media = [make_media(video=make_video(height=1080))]

        result = process_scale(ScaleVideoMode.P720, media, reject_increase=False)

        assert result == ["scale=-2:720"]

    def test_scale_equal_height_returns_none(self):
        media = [make_media(video=make_video(height=720))]

        result = process_scale(ScaleVideoMode.P720, media, reject_increase=False)

        assert result == [None]

    def test_scale_increase_rejected(self):
        media = [make_media(video=make_video(height=480))]

        result = process_scale(ScaleVideoMode.P720, media, reject_increase=True)

        assert result == [None]

    def test_scale_increase_allowed_when_not_rejected(self):
        media = [make_media(video=make_video(height=480))]

        result = process_scale(ScaleVideoMode.P720, media, reject_increase=False)

        assert result == ["scale=-2:720"]

    def test_scale_with_min_when_reject_increase(self):
        media = [make_media(video=make_video(height=1080))]

        result = process_scale(ScaleVideoMode.P720, media, reject_increase=True)

        assert result == ["scale=-2:min(720\\,ih)"]

    def test_scale_multiple_media(self):
        media = [
            make_media(video=make_video(height=1080)),
            make_media(video=make_video(height=720)),
        ]

        result = process_scale(ScaleVideoMode.P480, media, reject_increase=False)

        assert result == ["scale=-2:480", "scale=-2:480"]

    def test_scale_multiple_media_with_reject_increase(self):
        media = [
            make_media(video=make_video(height=1080)),
            make_media(video=make_video(height=480)),
        ]

        result = process_scale(ScaleVideoMode.P720, media, reject_increase=True)

        assert result == ["scale=-2:min(720\\,ih)", None]

    def test_scale_missing_height_raises(self):
        media = [make_media(video=make_video(height=None))]

        with pytest.raises(MissingMediaPropertyError):
            process_scale(ScaleVideoMode.P720, media, reject_increase=False)

    def test_scale_missing_video_raises(self):
        media = [make_media(video=None)]

        with pytest.raises(MissingMediaPropertyError):
            process_scale(ScaleVideoMode.P720, media, reject_increase=False)

    def test_scale_gif_mode(self):
        media = [make_media(video=make_video(height=1080))]

        result = process_scale(ScaleGifMode.P480, media, reject_increase=False)

        assert result == ["scale=-2:480"]


# -----------------------------------------------------------------------------
#  process_time()
# -----------------------------------------------------------------------------


class TestProcessTime:
    def test_valid_time(self):
        assert process_time("1:30", timedelta(hours=2)) == 90.0

    def test_valid_time_zero(self):
        assert process_time("0:00", timedelta(hours=1)) == 0.0

    def test_invalid_format_raises(self):
        with pytest.raises(InvalidTimeFormatError):
            process_time("abc", timedelta(hours=1))

    def test_negative_time_raises(self):
        # convert_to_timedelta returns None for negative times (isdigit() fails)
        # so process_time raises InvalidTimeFormatError instead of NegativeTimeError
        with pytest.raises(InvalidTimeFormatError):
            process_time("-1:00", timedelta(hours=1))

    def test_missing_duration_raises(self):
        with pytest.raises(MissingMediaPropertyError):
            process_time("1:00", None)

    def test_time_exceeds_duration_raises(self):
        with pytest.raises(TimeExceedsDurationError):
            process_time("2:00", timedelta(minutes=1))

    def test_time_equal_duration_ok(self):
        assert process_time("1:00", timedelta(minutes=1)) == 60.0


# -----------------------------------------------------------------------------
#  process_trim_points()
# -----------------------------------------------------------------------------


class TestProcessTrimPoints:
    def test_valid_trim_points(self):
        result = process_trim_points(
            "0:10,0:20,0:30", timedelta(minutes=1), Path("video.mp4")
        )

        assert result == "10.0,20.0,30.0"

    def test_single_trim_point(self):
        result = process_trim_points("0:15", timedelta(minutes=1), Path("video.mp4"))

        assert result == "15.0"

    def test_missing_duration_raises(self):
        with pytest.raises(MissingMediaError):
            process_trim_points("0:10", None, Path("video.mp4"))

    def test_invalid_format_raises(self):
        with pytest.raises(InvalidTimeFormatError):
            process_trim_points("abc", timedelta(minutes=1), Path("video.mp4"))

    def test_trim_point_exceeds_duration_raises(self):
        # process_trim_points raises TimeExceedsDurationError when a trim point
        # exceeds the video duration
        with pytest.raises(TimeExceedsDurationError):
            process_trim_points("2:00", timedelta(minutes=1), Path("video.mp4"))

    def test_trim_point_exactly_at_duration_ok(self):
        result = process_trim_points(
            "1:00", timedelta(minutes=1), Path("video.mp4")
        )

        assert result == "60.0"

    def test_empty_trim_points_raises(self):
        with pytest.raises(InvalidTimeFormatError):
            process_trim_points("", timedelta(minutes=1), Path("video.mp4"))