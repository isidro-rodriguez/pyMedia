"""Tests para los mixins de salida por tipo (pymedia.models.mixins.outputs_mixin)."""

from pathlib import Path

import pytest

from pymedia.errors import (
    InvalidArgumentError,
    InvalidContainerError,
    InvalidContainerTypeError,
    MissingMediaPropertyError,
)
from pymedia.models.media import Audio, Media, Video
from pymedia.models.mixins.outputs_mixin import (
    AnimatedOutputMixin,
    ImageOutputMixin,
    SubtitleOutputMixin,
    _process_output,
    _validate_name,
)
from pymedia.types import OutputMediaType


def _video(codec: str | None = "h264") -> Video:
    """Vídeo de ayuda con códec h264 por defecto."""
    return Video(codec=codec, width=1920, height=1080)


def _audio(codec: str | None = "aac") -> Audio:
    """Pista de audio de ayuda con códec aac por defecto."""
    return Audio(path=Path("clip.mp4"), codec=codec, sample_rate=48000, channels=2)


def _media_with_path(
    name: str = "clip.mp4",
    video: Video | None = None,
    audio: Audio | None = None,
) -> Media:
    """Media de ayuda con ruta y, opcionalmente, pistas de vídeo y audio."""
    return Media(
        path=Path(name),
        video=video,
        audio=[audio] if audio else None,
    )


def _animated_mixin(media: Media | None = None) -> AnimatedOutputMixin:
    """AnimatedOutputMixin con la media indicada."""
    mixin = AnimatedOutputMixin()
    mixin.media = media
    return mixin


def _image_mixin(media: Media | None = None) -> ImageOutputMixin:
    """ImageOutputMixin con la media indicada."""
    mixin = ImageOutputMixin()
    mixin.media = media
    return mixin


def _subtitle_mixin(media: Media | None = None) -> SubtitleOutputMixin:
    """SubtitleOutputMixin con la media indicada."""
    mixin = SubtitleOutputMixin()
    mixin.media = media
    return mixin


class TestAnimatedOutputMixin:
    """Pruebas del mixin de salida de imágenes animadas (GIF)."""

    def test_sets_animated_output(self, tmp_path):
        """Comprueba que se asigna la salida GIF al campo tipado."""
        mixin = _animated_mixin()

        mixin.create_animated_output(output=tmp_path / "out.gif")

        assert mixin.animated_output == (tmp_path / "out.gif").absolute()

    def test_invalid_extension_raises(self, tmp_path):
        """Comprueba que una extensión no GIF lanza un error."""
        mixin = _animated_mixin()

        with pytest.raises(InvalidContainerTypeError) as exc_info:
            mixin.create_animated_output(output=tmp_path / "out.png")

        assert "gif" in exc_info.value.message


class TestImageOutputMixin:
    """Pruebas del mixin de salida de imágenes."""

    def test_default_image_output_from_media(self, tmp_path, monkeypatch):
        """Comprueba que el nombre por defecto deriva de la media."""
        monkeypatch.chdir(tmp_path)
        mixin = _image_mixin(media=_media_with_path())

        mixin.create_image_output(extension=".jpg")

        assert mixin.image_output == (tmp_path / "clip.jpg").absolute()

    def test_sets_image_output(self, tmp_path):
        """Comprueba que se asigna la salida al campo tipado."""
        mixin = _image_mixin()

        mixin.create_image_output(output=tmp_path / "out.png")

        assert mixin.image_output == (tmp_path / "out.png").absolute()

    def test_invalid_extension_raises(self, tmp_path):
        """Comprueba que una extensión no de imagen lanza un error."""
        mixin = _image_mixin()

        with pytest.raises(InvalidContainerTypeError) as exc_info:
            mixin.create_image_output(output=tmp_path / "out.xyz")

        assert "Image" in exc_info.value.message

    def test_output_directory_created(self, tmp_path):
        """Comprueba que se crea y usa el directorio de salida."""
        target = tmp_path / "out"
        mixin = _image_mixin(media=_media_with_path())

        mixin.create_image_output(output_directory=target, extension=".jpg")

        assert mixin.output_directory == target
        assert mixin.image_output == (target / "clip.jpg").absolute()
        assert target.is_dir()

    def test_output_directory_invalid_name(self, tmp_path):
        """Comprueba que un nombre de directorio no válido lanza un error."""
        mixin = _image_mixin()

        with pytest.raises(InvalidArgumentError):
            mixin.create_image_output(output_directory=tmp_path / "out<bad>")
        assert mixin.image_output is None


class TestSubtitleOutputMixin:
    """Pruebas del mixin de salida de subtítulos."""

    def test_sets_subtitle_output(self, tmp_path):
        """Comprueba que se asigna la salida al campo tipado."""
        mixin = _subtitle_mixin()

        mixin.create_subtitle_output(output=tmp_path / "out.srt")

        assert mixin.subtitle_output == (tmp_path / "out.srt").absolute()

    def test_invalid_extension_raises(self, tmp_path):
        """Comprueba que una extensión no de subtítulo lanza un error."""
        mixin = _subtitle_mixin()

        with pytest.raises(InvalidContainerTypeError) as exc_info:
            mixin.create_subtitle_output(output=tmp_path / "out.xyz")

        assert "Subtitle" in exc_info.value.message


class TestProcessOutput:
    """Pruebas del procesamiento de la ruta de salida (función compartida)."""

    def test_default_path_uses_media_name(self, tmp_path, monkeypatch):
        """Comprueba que la salida por defecto usa el nombre de la media."""
        monkeypatch.chdir(tmp_path)

        output = _process_output(
            _media_with_path(),
            OutputMediaType.GIF,
            extension=".gif",
        )

        assert output == (tmp_path / "clip.gif").absolute()

    def test_affix_and_extension_applied(self, tmp_path, monkeypatch):
        """Comprueba que se aplican el sufijo y la extensión indicados."""
        monkeypatch.chdir(tmp_path)

        output = _process_output(
            _media_with_path(),
            OutputMediaType.GIF,
            affix="_edit",
            extension=".gif",
        )

        assert output == (tmp_path / "clip_edit.gif").absolute()

    def test_explicit_output_ignores_affix(self, tmp_path):
        """Comprueba que una ruta explícita ignora el sufijo."""
        explicit = tmp_path / "done.gif"

        output = _process_output(
            _media_with_path(),
            OutputMediaType.GIF,
            affix="_x",
            extension=".gif",
            output=explicit,
        )

        assert output == explicit.absolute()

    def test_output_directory_used_as_parent(self, tmp_path):
        """Comprueba que el directorio es el padre de la salida por defecto."""
        target = tmp_path / "out"

        output = _process_output(
            _media_with_path(),
            OutputMediaType.GIF,
            output_directory=target,
            extension=".gif",
        )

        assert output == (target / "clip.gif").absolute()


class TestValidateOutput:
    """Pruebas de validación de la extensión según el tipo de medio."""

    def test_gif_valid_extension(self, tmp_path):
        """Comprueba que una extensión GIF válida se acepta."""
        output = _process_output(
            _media_with_path(), OutputMediaType.GIF, output=tmp_path / "out.gif"
        )
        assert output == (tmp_path / "out.gif").absolute()

    def test_gif_invalid_extension(self, tmp_path):
        """Comprueba que una extensión no GIF lanza un error."""
        with pytest.raises(InvalidContainerTypeError) as exc_info:
            _process_output(
                _media_with_path(), OutputMediaType.GIF, output=tmp_path / "out.png"
            )
        assert "gif" in exc_info.value.message

    def test_image_invalid_extension(self, tmp_path):
        """Comprueba que una extensión no de imagen lanza un error."""
        with pytest.raises(InvalidContainerTypeError) as exc_info:
            _process_output(
                _media_with_path(),
                OutputMediaType.IMAGE,
                output=tmp_path / "out.xyz",
            )
        assert "Image" in exc_info.value.message

    def test_audio_requires_track(self, tmp_path):
        """Comprueba que la salida de audio exige una pista de audio."""
        with pytest.raises(MissingMediaPropertyError, match="audio track"):
            _process_output(
                _media_with_path(),
                OutputMediaType.AUDIO,
                output=tmp_path / "out.m4a",
            )

    def test_audio_valid_extension(self, tmp_path):
        """Comprueba que una extensión de audio válida se acepta."""
        output = _process_output(
            _media_with_path(audio=_audio("aac")),
            OutputMediaType.AUDIO,
            output=tmp_path / "out.m4a",
        )
        assert output == (tmp_path / "out.m4a").absolute()

    def test_audio_extension_not_supported_by_codec(self, tmp_path):
        """Comprueba que un códec que no soporta la extensión lanza un error."""
        with pytest.raises(InvalidContainerError):
            _process_output(
                _media_with_path(audio=_audio("aac")),
                OutputMediaType.AUDIO,
                output=tmp_path / "out.flac",
            )

    def test_audio_not_container_extension(self, tmp_path):
        """Comprueba que una extensión no de audio lanza un error."""
        with pytest.raises(InvalidContainerTypeError):
            _process_output(
                _media_with_path(audio=_audio("aac")),
                OutputMediaType.AUDIO,
                output=tmp_path / "out.txt",
            )

    def test_subtitle_invalid_extension(self, tmp_path):
        """Comprueba que una extensión no de subtítulo lanza un error."""
        with pytest.raises(InvalidContainerTypeError) as exc_info:
            _process_output(
                _media_with_path(),
                OutputMediaType.SUBTITLE,
                output=tmp_path / "out.xyz",
            )
        assert "Subtitle" in exc_info.value.message

    def test_video_requires_track(self, tmp_path):
        """Comprueba que la salida de vídeo exige una pista de vídeo."""
        with pytest.raises(MissingMediaPropertyError, match="video"):
            _process_output(
                _media_with_path(),
                OutputMediaType.VIDEO,
                output=tmp_path / "out.mp4",
            )

    def test_video_requires_codec(self, tmp_path):
        """Comprueba que la salida de vídeo exige un códec en la pista."""
        with pytest.raises(MissingMediaPropertyError, match="video codec"):
            _process_output(
                _media_with_path(video=_video(None)),
                OutputMediaType.VIDEO,
                output=tmp_path / "out.mp4",
            )

    def test_video_valid_extension(self, tmp_path):
        """Comprueba que una extensión de vídeo válida se acepta."""
        output = _process_output(
            _media_with_path(video=_video("h264")),
            OutputMediaType.VIDEO,
            output=tmp_path / "out.mp4",
        )
        assert output == (tmp_path / "out.mp4").absolute()

    def test_video_extension_not_supported_by_codec(self, tmp_path):
        """Comprueba que un códec que no soporta la extensión lanza un error."""
        with pytest.raises(InvalidContainerError) as exc_info:
            _process_output(
                _media_with_path(video=_video("h264")),
                OutputMediaType.VIDEO,
                output=tmp_path / "out.avi",
            )
        assert "h264" in exc_info.value.message

    def test_video_not_container_extension(self, tmp_path):
        """Comprueba el error cuando la extensión no es contenedor de vídeo."""
        with pytest.raises(InvalidContainerTypeError):
            _process_output(
                _media_with_path(video=_video("h264")),
                OutputMediaType.VIDEO,
                output=tmp_path / "out.txt",
            )

    def test_video_audio_codec_checked(self, tmp_path):
        """Comprueba que el contenedor de vídeo también soporta los códecs de audio."""
        # .m2ts es válido para h264 pero no para aac
        with pytest.raises(InvalidContainerError):
            _process_output(
                _media_with_path(video=_video("h264"), audio=_audio("aac")),
                OutputMediaType.VIDEO,
                output=tmp_path / "out.m2ts",
            )


class TestValidateName:
    """Pruebas de validación de nombres de fichero."""

    @pytest.mark.parametrize("name", ["clip", "clip final", "Clip-01_v2", "vídeo ñ"])
    def test_valid_names_do_not_raise(self, name):
        """Comprueba que los nombres válidos no lanzan errores."""
        _validate_name(name)

    @pytest.mark.parametrize(
        "name",
        ["a<b", "a>b", "a:b", 'a"b', "a/b", "a\\b", "a|b", "a?b", "a*b", "a\x00b"],
    )
    def test_invalid_characters(self, name):
        """Comprueba que los caracteres no permitidos lanzan un error."""
        with pytest.raises(InvalidArgumentError):
            _validate_name(name)

    @pytest.mark.parametrize(
        "name", ["CON", "con", "PRN", "AUX", "NUL", "LPT1", "COM9"]
    )
    def test_reserved_names(self, name):
        """Comprueba que los nombres reservados de Windows lanzan un error."""
        with pytest.raises(InvalidArgumentError):
            _validate_name(name)

    @pytest.mark.parametrize("name", ["clip ", "clip."])
    def test_trailing_space_or_dot(self, name):
        """Comprueba que un espacio o punto final lanzan un error."""
        with pytest.raises(InvalidArgumentError):
            _validate_name(name)

    def test_empty_name(self):
        """Comprueba que un nombre vacío lanza un error."""
        with pytest.raises(InvalidArgumentError):
            _validate_name("")
