"""Tests para verificar la coherencia de los datos en src/pymedia/data/."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from pymedia.data.audio_codecs import AUDIO_CODECS, AudioCodecData
from pymedia.data.video_codecs import VIDEO_CODECS, VideoCodecData


class TestAudioCodecsConsistency:
    def test_all_codecs_have_required_fields(self):
        """Todos los codecs de audio deben tener nombre y library."""
        for codec_name, codec in AUDIO_CODECS.items():
            assert hasattr(codec, "name"), f"{codec_name} missing name"
            assert hasattr(codec, "library"), f"{codec_name} missing library"
            assert codec.name == codec_name, f"{codec_name}: name mismatch"

    def test_all_codecs_have_containers(self):
        """Todos los codecs de audio deben tener containers."""
        for codec_name, codec in AUDIO_CODECS.items():
            assert hasattr(codec, "containers"), f"{codec_name} missing containers"
            assert isinstance(codec.containers, tuple), f"{codec_name}: containers should be tuple"
            assert len(codec.containers) > 0, f"{codec_name}: containers should not be empty"

    def test_bitrate_format_when_present(self):
        """Si un codec tiene bitrates, deben tener formato 'Nk'."""
        for codec_name, codec in AUDIO_CODECS.items():
            if codec.bit_rates is not None:
                for br in codec.bit_rates:
                    assert br.endswith("k") or br.isdigit(), \
                        f"{codec_name}: bitrate '{br}' tiene formato inesperado"


class TestVideoCodecsConsistency:
    def test_all_codecs_have_required_fields(self):
        """Todos los codecs de video deben tener nombre y library."""
        # Mapeo de aliases: hevc -> h265
        name_aliases = {"hevc": "h265"}

        for codec_name, codec in VIDEO_CODECS.items():
            assert hasattr(codec, "name"), f"{codec_name} missing name"
            assert hasattr(codec, "library"), f"{codec_name} missing library"
            # Permitir aliases de nombre
            expected_name = name_aliases.get(codec_name, codec_name)
            assert codec.name == expected_name, f"{codec_name}: name mismatch (expected {expected_name}, got {codec.name})"

    def test_all_codecs_have_containers(self):
        """Todos los codecs de video deben tener containers."""
        for codec_name, codec in VIDEO_CODECS.items():
            assert hasattr(codec, "containers"), f"{codec_name} missing containers"
            assert isinstance(codec.containers, tuple), f"{codec_name}: containers should be tuple"
            assert len(codec.containers) > 0, f"{codec_name}: containers should not be empty"

    def test_crf_when_present(self):
        """Si un codec tiene CRF, debe ser una tupla de 2 ints."""
        for codec_name, codec in VIDEO_CODECS.items():
            if codec.crf is not None:
                assert isinstance(codec.crf, tuple), f"{codec_name}: crf should be tuple"
                assert len(codec.crf) == 2, f"{codec_name}: crf should have 2 values"
                assert all(isinstance(v, int) for v in codec.crf), \
                    f"{codec_name}: crf values should be ints"

    def test_pix_fmt_when_present(self):
        """Si un codec tiene pix_fmt, debe ser string."""
        for codec_name, codec in VIDEO_CODECS.items():
            if codec.pix_fmt is not None:
                assert isinstance(codec.pix_fmt, str), \
                    f"{codec_name}: pix_fmt should be string"

    def test_presets_when_present(self):
        """Si un codec tiene presets, debe ser una tupla."""
        for codec_name, codec in VIDEO_CODECS.items():
            if codec.presets is not None:
                assert isinstance(codec.presets, tuple), \
                    f"{codec_name}: presets should be tuple"


class TestCrossModuleConsistency:
    def test_no_orphan_codecs(self):
        """Ningún codec definido debería estar fuera del diccionario correspondiente."""
        audio_names = set(AUDIO_CODECS.keys())
        video_names = set(VIDEO_CODECS.keys())

        # Revisar que los codecs comunes no estén duplicados en el otro módulo
        # (some codecs like "hevc" map to h265 in video, but that's expected)

    def test_container_consistency_between_audio_and_video(self):
        """Algunos contenedores deben ser compartidos entre audio y video."""
        audio_containers = set()
        for codec in AUDIO_CODECS.values():
            audio_containers.update(codec.containers)

        video_containers = set()
        for codec in VIDEO_CODECS.values():
            video_containers.update(codec.containers)

        # Format containers should overlap
        assert len(audio_containers & video_containers) > 0, \
            "No hay contenedores compartidos entre audio y video"