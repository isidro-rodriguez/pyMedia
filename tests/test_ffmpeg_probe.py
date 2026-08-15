"""Tests para el probe de ffmpeg (pymedia.ffmpeg.probe)."""

import json
import subprocess
from pathlib import Path

import pytest

from pymedia.ffmpeg.probe import probe


class TestProbe:
    def test_probe_returns_parsed_json(self, monkeypatch):
        expected = {
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": "h264",
                    "width": 1920,
                    "height": 1080,
                }
            ],
            "format": {"duration": "60.0", "format_name": "mp4"},
        }

        def fake_run(cmd, **kwargs):
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=0,
                stdout=json.dumps(expected),
                stderr="",
            )

        monkeypatch.setattr("subprocess.run", fake_run)

        result = probe(Path("video.mp4"))

        assert result == expected

    def test_probe_empty_streams(self, monkeypatch):
        expected = {"streams": [], "format": {}}

        def fake_run(cmd, **kwargs):
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=0,
                stdout=json.dumps(expected),
                stderr="",
            )

        monkeypatch.setattr("subprocess.run", fake_run)

        result = probe(Path("video.mp4"))

        assert result == {"streams": [], "format": {}}

    def test_probe_raises_on_ffprobe_not_found(self, monkeypatch):
        def fake_run(cmd, **kwargs):
            raise FileNotFoundError("ffprobe not found")

        monkeypatch.setattr("subprocess.run", fake_run)

        with pytest.raises(FileNotFoundError):
            probe(Path("video.mp4"))

    def test_probe_passes_correct_arguments(self, monkeypatch):
        captured = {}

        def fake_run(cmd, **kwargs):
            captured["cmd"] = cmd
            captured["capture_output"] = kwargs.get("capture_output")
            captured["text"] = kwargs.get("text")
            captured["check"] = kwargs.get("check")
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=0,
                stdout="{}",
                stderr="",
            )

        monkeypatch.setattr("subprocess.run", fake_run)

        probe(Path("input.mkv"))

        assert captured["cmd"] == [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            "input.mkv",
        ]
        assert captured["capture_output"] is True
        assert captured["text"] is True
        assert captured["check"] is True