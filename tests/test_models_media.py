"""Tests para el modelo de media (pymedia.models.media)."""

from datetime import timedelta
from fractions import Fraction
from pathlib import Path

from pymedia.models.media import Audio, Media, Video


class TestVideo:
    def test_default_values(self):
        video = Video()

        assert video.codec is None
        assert video.width is None
        assert video.height is None
        assert video.fps is None
        assert video.bit_rate is None
        assert video.pix_fmt is None
        assert video.aspect_ratio is None


class TestAudio:
    def test_default_values(self):
        audio = Audio()

        assert audio.codec is None
        assert audio.sample_rate is None
        assert audio.channels is None
        assert audio.channel_layout is None
        assert audio.bit_rate is None
        assert audio.language is None


class TestMedia:
    def test_default_values(self):
        media = Media()

        assert media.duration is None
        assert media.size is None
        assert media.format_name is None
        assert media.video is None
        assert media.audio is None


class TestMediaLoad:
    def _fake_probe(self, data):
        def probe(path):
            return data

        return probe

    def test_load_with_video_and_audio(self, monkeypatch):
        data = {
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": "h264",
                    "width": 1920,
                    "height": 1080,
                    "avg_frame_rate": "30000/1001",
                    "bit_rate": "1000000",
                    "pix_fmt": "yuv420p",
                    "display_aspect_ratio": "16:9",
                },
                {
                    "codec_type": "audio",
                    "codec_name": "aac",
                    "sample_rate": "48000",
                    "channels": 2,
                    "channel_layout": "stereo",
                    "bit_rate": "128000",
                    "tags": {"language": "eng"},
                },
            ],
            "format": {
                "duration": "60.5",
                "size": "1234567",
                "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
            },
        }
        monkeypatch.setattr(
            "pymedia.models.media.ffprobe", self._fake_probe(data)
        )

        media = Media.load(Path("video.mp4"))

        assert media.duration == timedelta(seconds=60.5)
        assert media.size == 1234567
        assert media.format_name == "mov,mp4,m4a,3gp,3g2,mj2"

        assert media.video is not None
        assert media.video.codec == "h264"
        assert media.video.width == 1920
        assert media.video.height == 1080
        assert media.video.fps == Fraction(30000, 1001)
        assert media.video.bit_rate == 1000000
        assert media.video.pix_fmt == "yuv420p"
        assert media.video.aspect_ratio == "16:9"

        assert media.audio is not None
        assert media.audio.codec == "aac"
        assert media.audio.sample_rate == 48000
        assert media.audio.channels == 2
        assert media.audio.channel_layout == "stereo"
        assert media.audio.bit_rate == 128000
        assert media.audio.language == "eng"

    def test_load_without_streams(self, monkeypatch):
        data = {"streams": [], "format": {}}
        monkeypatch.setattr(
            "pymedia.models.media.ffprobe", self._fake_probe(data)
        )

        media = Media.load(Path("video.mp4"))

        assert media.video is None
        assert media.audio is None
        assert media.duration is None
        assert media.size is None
        assert media.format_name is None

    def test_load_video_only(self, monkeypatch):
        data = {
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": "h264",
                    "width": 1280,
                    "height": 720,
                    "avg_frame_rate": "25/1",
                    "bit_rate": "500000",
                    "pix_fmt": "yuv420p",
                    "display_aspect_ratio": "16:9",
                }
            ],
            "format": {"duration": "10.0", "size": "1000", "format_name": "mp4"},
        }
        monkeypatch.setattr(
            "pymedia.models.media.ffprobe", self._fake_probe(data)
        )

        media = Media.load(Path("video.mp4"))

        assert media.video is not None
        assert media.audio is None

    def test_load_audio_only(self, monkeypatch):
        data = {
            "streams": [
                {
                    "codec_type": "audio",
                    "codec_name": "mp3",
                    "sample_rate": "44100",
                    "channels": 2,
                    "channel_layout": "stereo",
                    "bit_rate": "128000",
                    "tags": {"language": "spa"},
                }
            ],
            "format": {"duration": "3.0", "size": "500", "format_name": "mp3"},
        }
        monkeypatch.setattr(
            "pymedia.models.media.ffprobe", self._fake_probe(data)
        )

        media = Media.load(Path("audio.mp3"))

        assert media.video is None
        assert media.audio is not None
        assert media.audio.codec == "mp3"
        assert media.audio.language == "spa"

    def test_load_missing_duration(self, monkeypatch):
        data = {
            "streams": [],
            "format": {"size": "100", "format_name": "mp4"},
        }
        monkeypatch.setattr(
            "pymedia.models.media.ffprobe", self._fake_probe(data)
        )

        media = Media.load(Path("video.mp4"))

        assert media.duration is None

    def test_load_invalid_fps(self, monkeypatch):
        data = {
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": "h264",
                    "width": 1920,
                    "height": 1080,
                    "avg_frame_rate": "abc",
                    "bit_rate": "1000000",
                    "pix_fmt": "yuv420p",
                    "display_aspect_ratio": "16:9",
                }
            ],
            "format": {"duration": "60.0", "size": "1000", "format_name": "mp4"},
        }
        monkeypatch.setattr(
            "pymedia.models.media.ffprobe", self._fake_probe(data)
        )

        media = Media.load(Path("video.mp4"))

        assert media.video is not None
        assert media.video.fps is None


class TestConcatSignature:
    def _make_media(self, video=None, audio=None):
        return Media(video=video, audio=audio)

    def test_signature_with_video_and_audio(self):
        video = Video(
            codec="h264",
            width=1920,
            height=1080,
            fps=Fraction(25, 1),
            pix_fmt="yuv420p",
            aspect_ratio="16:9",
        )
        audio = Audio(
            codec="aac",
            sample_rate=48000,
            channels=2,
            channel_layout="stereo",
        )

        media = self._make_media(video=video, audio=audio)

        assert media.concat_signature == (
            ("h264", 1920, 1080, Fraction(25, 1), "yuv420p", "16:9"),
            ("aac", 48000, 2, "stereo"),
        )

    def test_signature_without_video(self):
        audio = Audio(codec="aac", sample_rate=48000, channels=2, channel_layout="stereo")

        media = self._make_media(video=None, audio=audio)

        assert media.concat_signature == (None, ("aac", 48000, 2, "stereo"))

    def test_signature_without_audio(self):
        video = Video(codec="h264", width=1920, height=1080)

        media = self._make_media(video=video, audio=None)

        assert media.concat_signature == (("h264", 1920, 1080, None, None, None), None)

    def test_signature_equal_for_same_codecs(self):
        v1 = Video(codec="h264", width=1920, height=1080)
        v2 = Video(codec="h264", width=1920, height=1080)

        m1 = self._make_media(video=v1)
        m2 = self._make_media(video=v2)

        assert m1.concat_signature == m2.concat_signature

    def test_signature_differs_for_different_codecs(self):
        v1 = Video(codec="h264", width=1920, height=1080)
        v2 = Video(codec="h265", width=1920, height=1080)

        m1 = self._make_media(video=v1)
        m2 = self._make_media(video=v2)

        assert m1.concat_signature != m2.concat_signature