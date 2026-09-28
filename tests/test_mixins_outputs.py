"""Tests para los mixins de salida por tipo (pymedia.mixins.outputs_mixin)."""

from pathlib import Path

import pytest

from pymedia.errors import MissingPropertyError, UserError
from pymedia.mixins.outputs_mixin import (
    AnimatedOutputMixin,
    AudioOutputMixin,
    ImageOutputMixin,
    MediaOutputMixin,
    SubtitlesOutputMixin,
    _process_output,
    _process_output_directory,
    _validate_name,
)
from pymedia.models.audio import AudioFormat
from pymedia.models.media import Audio, Media, Subtitles, Video
from pymedia.models.subtitles import SubtitlesFormat
from pymedia.models.video import VideoFormat


def _video(codec: str | None = "h264") -> Video:
    """Vídeo de ayuda con códec h264 por defecto."""
    return Video(
        path=Path("clip.mp4"),
        format=VideoFormat(codec=codec, width=1920, height=1080),
    )


def _audio(codec: str | None = "aac") -> Audio:
    """Pista de audio de ayuda con códec aac por defecto."""
    return Audio(
        path=Path("clip.mp4"),
        format=AudioFormat(codec=codec, sample_rate=48000, channels=2),
    )


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


def _audio_mixin(media: Media | None = None) -> AudioOutputMixin:
    """AudioOutputMixin con la media indicada."""
    mixin = AudioOutputMixin()
    mixin.media = media
    return mixin


def _audio_track(codec: str, track_index: int) -> Audio:
    """Pista de audio de ayuda con códec e índice concretos."""
    return Audio(
        path=Path("clip.mkv"),
        track_index=track_index,
        format=AudioFormat(codec=codec, sample_rate=48000, channels=2),
    )


def _media_tracks(*audio_tracks: Audio) -> Media:
    """Media de ayuda con varias pistas de audio."""
    return Media(path=Path("clip.mkv"), audio=list(audio_tracks))


def _subtitles_track(codec: str | None, track_index: int) -> Subtitles:
    """Pista de subtítulos de ayuda con códec e índice concretos."""
    return Subtitles(
        path=Path("clip.mkv"),
        track_index=track_index,
        format=SubtitlesFormat(codec=codec),
    )


def _media_sub_tracks(*subtitles_tracks: Subtitles) -> Media:
    """Media de ayuda con varias pistas de subtítulos."""
    return Media(path=Path("clip.mkv"), subtitles=list(subtitles_tracks))


def _image_mixin(media: Media | None = None) -> ImageOutputMixin:
    """ImageOutputMixin con la media indicada."""
    mixin = ImageOutputMixin()
    mixin.media = media
    return mixin


def _media_mixin(media: Media | None = None) -> MediaOutputMixin:
    """MediaOutputMixin con la media indicada."""
    mixin = MediaOutputMixin()
    mixin.media = media
    return mixin


def _subtitles_mixin(media: Media | None = None) -> SubtitlesOutputMixin:
    """SubtitlesOutputMixin con la media indicada."""
    mixin = SubtitlesOutputMixin()
    mixin.media = media
    return mixin


class TestAnimatedOutputMixin:
    """Pruebas del mixin de salida de imágenes animadas (GIF)."""

    def test_sets_animated_output(self, tmp_path: Path) -> None:
        """Comprueba que se asigna la salida GIF al campo tipado."""
        mixin = _animated_mixin(media=_media_with_path())

        mixin.create_animated_output(extension=".gif", output=tmp_path / "out.gif")

        assert mixin.animated_output == (tmp_path / "out.gif").absolute()

    def test_invalid_extension_raises(self, tmp_path: Path) -> None:
        """Comprueba que una extensión no GIF lanza un error."""
        mixin = _animated_mixin(media=_media_with_path())

        with pytest.raises(UserError) as exc_info:
            mixin.create_animated_output(extension=".gif", output=tmp_path / "out.png")

        assert "gif" in str(exc_info.value)

    def test_output_directory_created(self, tmp_path: Path) -> None:
        """Comprueba que se crea y usa el directorio de salida."""
        target = tmp_path / "out"
        mixin = _animated_mixin(media=_media_with_path())

        mixin.create_animated_output(
            extension=".gif", output_directory=target, affix="_anim"
        )

        assert mixin.output_directory == target
        assert mixin.animated_output == (target / "clip_anim.gif").absolute()
        assert target.is_dir()


class TestAudioOutputMixin:
    """Pruebas del mixin de salida de pistas de audio."""

    def test_requires_audio_track(self, tmp_path: Path) -> None:
        """Comprueba que la salida de audio exige una pista de audio."""
        mixin = _audio_mixin(media=_media_with_path())

        with pytest.raises(MissingPropertyError, match="audio"):
            mixin.create_audio_output(extension=".m4a", output=tmp_path / "out.m4a")

    def test_requires_codec(self, tmp_path: Path) -> None:
        """Comprueba que la salida de audio exige un códec en la pista."""
        mixin = _audio_mixin(media=_media_with_path(audio=_audio(None)))

        with pytest.raises(MissingPropertyError, match="audio codec"):
            mixin.create_audio_output(extension=".m4a", output=tmp_path / "out.m4a")

    def test_sets_audio_output(self, tmp_path: Path) -> None:
        """Comprueba que se asigna la salida al campo tipado."""
        mixin = _audio_mixin(media=_media_with_path(audio=_audio("aac")))

        mixin.create_audio_output(extension=".m4a", output=tmp_path / "out.m4a")

        assert mixin.audio_output == (tmp_path / "out.m4a").absolute()

    def test_extension_not_supported_by_codec(self, tmp_path: Path) -> None:
        """Comprueba que un códec que no soporta la extensión lanza un error."""
        mixin = _audio_mixin(media=_media_with_path(audio=_audio("aac")))

        # .ogg es un destino de audio soportado, pero no admite aac
        with pytest.raises(UserError) as exc_info:
            mixin.create_audio_output(extension=".ogg", output=tmp_path / "out.ogg")

        assert "aac" in str(exc_info.value)

    def test_not_audio_extension(self, tmp_path: Path) -> None:
        """Comprueba que una extensión no de audio lanza un error."""
        mixin = _audio_mixin(media=_media_with_path(audio=_audio("aac")))

        with pytest.raises(UserError):
            mixin.create_audio_output(extension=".m4a", output=tmp_path / "out.txt")

    def test_ignores_unselected_tracks(self, tmp_path: Path) -> None:
        """Comprueba que solo se validan las pistas seleccionadas en stream_tracks."""
        mixin = _audio_mixin(
            media=_media_tracks(_audio_track("aac", 0), _audio_track("ac3", 1))
        )
        mixin.stream_tracks = [0]

        mixin.create_audio_output(extension=".m4a", output=tmp_path / "out.m4a")

        assert mixin.audio_output == (tmp_path / "out.m4a").absolute()

    def test_selected_track_codec_still_checked(self, tmp_path: Path) -> None:
        """Comprueba que el contenedor se valida contra la pista seleccionada."""
        mixin = _audio_mixin(
            media=_media_tracks(_audio_track("aac", 0), _audio_track("ac3", 1))
        )
        mixin.stream_tracks = [0]

        with pytest.raises(UserError) as exc_info:
            mixin.create_audio_output(extension=".ogg", output=tmp_path / "out.ogg")

        assert "aac" in str(exc_info.value)

    def test_all_tracks_checked_without_selection(self, tmp_path: Path) -> None:
        """Comprueba que sin selección se validan todas las pistas de la media."""
        mixin = _audio_mixin(
            media=_media_tracks(_audio_track("aac", 0), _audio_track("ac3", 1))
        )

        with pytest.raises(UserError) as exc_info:
            mixin.create_audio_output(extension=".m4a", output=tmp_path / "out.m4a")

        assert "ac3" in str(exc_info.value)

    def test_remux_to_safe_container(self, tmp_path: Path) -> None:
        """Comprueba que un cambio de contenedor seguro para el códec pasa."""
        mixin = _audio_mixin(media=_media_tracks(_audio_track("opus", 0)))

        mixin.create_audio_output(extension=".ogg", output=tmp_path / "out.ogg")

        assert mixin.audio_output == (tmp_path / "out.ogg").absolute()

    def test_remux_to_unsafe_container_raises(self, tmp_path: Path) -> None:
        """Comprueba que el remux a un contenedor no seguro lanza un error."""
        mixin = _audio_mixin(media=_media_tracks(_audio_track("aac", 0)))

        with pytest.raises(UserError) as exc_info:
            mixin.create_audio_output(extension=".ogg", output=tmp_path / "out.ogg")

        assert "aac" in str(exc_info.value)
        assert ".m4a" in str(exc_info.value)

    def test_remux_error_lists_safe_targets(self, tmp_path: Path) -> None:
        """Comprueba que el error de remux lista los destinos seguros del códec."""
        mixin = _audio_mixin(media=_media_tracks(_audio_track("ac3", 0)))

        with pytest.raises(UserError) as exc_info:
            mixin.create_audio_output(extension=".m4a", output=tmp_path / "out.m4a")

        assert "ac3" in str(exc_info.value)
        assert ".m2ts" in str(exc_info.value)

    def test_remux_ignores_unselected_tracks(self, tmp_path: Path) -> None:
        """Comprueba que el remux solo se valida contra las pistas seleccionadas."""
        mixin = _audio_mixin(
            media=_media_tracks(_audio_track("opus", 0), _audio_track("aac", 1))
        )
        mixin.stream_tracks = [0]

        mixin.create_audio_output(extension=".ogg", output=tmp_path / "out.ogg")

        assert mixin.audio_output == (tmp_path / "out.ogg").absolute()

    def test_output_directory_created_and_used(self, tmp_path: Path) -> None:
        """Comprueba que se crea y usa el directorio de salida del lote."""
        target = tmp_path / "audio"
        mixin = _audio_mixin(media=_media_tracks(_audio_track("aac", 0)))

        mixin.create_audio_output(extension=".m4a", output_directory=target)

        assert mixin.output_directory == target
        assert mixin.audio_output == (target / "clip.m4a").absolute()
        assert target.is_dir()


class TestImageOutputMixin:
    """Pruebas del mixin de salida de imágenes."""

    def test_default_image_output_from_media(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Comprueba que el nombre por defecto deriva de la media."""
        monkeypatch.chdir(tmp_path)
        mixin = _image_mixin(media=_media_with_path())

        mixin.create_image_output(extension=".jpg")

        assert mixin.image_output == (tmp_path / "clip.jpg").absolute()

    def test_sets_image_output(self, tmp_path: Path) -> None:
        """Comprueba que se asigna la salida al campo tipado."""
        mixin = _image_mixin(media=_media_with_path())

        mixin.create_image_output(extension=".png", output=tmp_path / "out.png")

        assert mixin.image_output == (tmp_path / "out.png").absolute()

    def test_invalid_extension_raises(self, tmp_path: Path) -> None:
        """Comprueba que una extensión no de imagen lanza un error."""
        mixin = _image_mixin(media=_media_with_path())

        with pytest.raises(UserError) as exc_info:
            mixin.create_image_output(extension=".png", output=tmp_path / "out.xyz")

        assert ".xyz" in str(exc_info.value)

    def test_output_directory_created(self, tmp_path: Path) -> None:
        """Comprueba que se crea y usa el directorio de salida."""
        target = tmp_path / "out"
        mixin = _image_mixin(media=_media_with_path())

        mixin.create_image_output(extension=".jpg", output_directory=target)

        assert mixin.output_directory == target
        assert mixin.image_output == (target / "clip.jpg").absolute()
        assert target.is_dir()

    def test_output_directory_invalid_name(self, tmp_path: Path) -> None:
        """Comprueba que un nombre de directorio no válido lanza un error."""
        mixin = _image_mixin(media=_media_with_path())

        with pytest.raises(UserError):
            mixin.create_image_output(
                extension=".jpg", output_directory=tmp_path / "out<bad>"
            )
        assert mixin.image_output is None


class TestSubtitlesOutputMixin:
    """Pruebas del mixin de salida de subtítulos."""

    def test_sets_subtitles_output(self, tmp_path: Path) -> None:
        """Comprueba que se asigna la salida al campo tipado."""
        mixin = _subtitles_mixin(media=_media_sub_tracks(_subtitles_track("srt", 0)))

        mixin.create_subtitles_output(extension=".srt", output=tmp_path / "out.srt")

        assert mixin.subtitles_output == (tmp_path / "out.srt").absolute()

    def test_invalid_extension_raises(self, tmp_path: Path) -> None:
        """Comprueba que una extensión no de subtítulo lanza un error."""
        mixin = _subtitles_mixin(media=_media_sub_tracks(_subtitles_track("srt", 0)))

        with pytest.raises(UserError) as exc_info:
            mixin.create_subtitles_output(extension=".srt", output=tmp_path / "out.xyz")

        assert ".xyz" in str(exc_info.value)

    def test_remux_to_safe_container(self, tmp_path: Path) -> None:
        """Comprueba que extraer srt a .srt desde un mkv pasa la validación."""
        mixin = _subtitles_mixin(media=_media_sub_tracks(_subtitles_track("srt", 0)))

        mixin.create_subtitles_output(extension=".srt", output=tmp_path / "out.srt")

        assert mixin.subtitles_output == (tmp_path / "out.srt").absolute()

    def test_remux_to_unsafe_container_raises(self, tmp_path: Path) -> None:
        """Comprueba que cambiar srt a .ass lanza un error."""
        mixin = _subtitles_mixin(media=_media_sub_tracks(_subtitles_track("srt", 0)))

        with pytest.raises(UserError) as exc_info:
            mixin.create_subtitles_output(extension=".ass", output=tmp_path / "out.ass")

        assert "srt" in str(exc_info.value)

    def test_remux_reverse_direction_rejected(self, tmp_path: Path) -> None:
        """Comprueba que cambiar ass a .srt también se rechaza."""
        mixin = _subtitles_mixin(media=_media_sub_tracks(_subtitles_track("ass", 0)))

        with pytest.raises(UserError) as exc_info:
            mixin.create_subtitles_output(extension=".srt", output=tmp_path / "out.srt")

        assert "ass" in str(exc_info.value)

    def test_remux_ignores_unselected_tracks(self, tmp_path: Path) -> None:
        """Comprueba que el remux solo se valida contra las pistas seleccionadas."""
        mixin = _subtitles_mixin(
            media=_media_sub_tracks(
                _subtitles_track("ass", 0), _subtitles_track("srt", 1)
            )
        )
        mixin.stream_tracks = [0]

        mixin.create_subtitles_output(extension=".ass", output=tmp_path / "out.ass")

        assert mixin.subtitles_output == (tmp_path / "out.ass").absolute()

    def test_output_directory_created_and_used(self, tmp_path: Path) -> None:
        """Comprueba que se crea y usa el directorio de salida del lote."""
        target = tmp_path / "subs"
        mixin = _subtitles_mixin(media=_media_sub_tracks(_subtitles_track("srt", 0)))

        mixin.create_subtitles_output(extension=".srt", output_directory=target)

        assert mixin.output_directory == target
        assert mixin.subtitles_output == (target / "clip.srt").absolute()
        assert target.is_dir()

    def test_requires_subtitles_track(self, tmp_path: Path) -> None:
        """Comprueba que la salida de subtítulos exige pistas en el medio."""
        mixin = _subtitles_mixin(media=Media(path=Path("clip.mkv"), subtitles=None))

        with pytest.raises(MissingPropertyError, match="subtitles"):
            mixin.create_subtitles_output(extension=".srt", output=tmp_path / "out.srt")

    def test_requires_codec(self, tmp_path: Path) -> None:
        """Comprueba que la salida de subtítulos exige códec en cada pista."""
        mixin = _subtitles_mixin(media=_media_sub_tracks(_subtitles_track(None, 0)))

        with pytest.raises(MissingPropertyError, match="subtitles codec"):
            mixin.create_subtitles_output(extension=".srt", output=tmp_path / "out.srt")


class TestProcessOutputDirectory:
    """Pruebas de creación del directorio de salida (función compartida)."""

    def test_creates_nested_directories(self, tmp_path: Path) -> None:
        """Comprueba que se crean los directorios intermedios que falten."""
        target = tmp_path / "a" / "b" / "c"

        assert _process_output_directory(target) == target
        assert target.is_dir()

    def test_reuses_existing_directory(self, tmp_path: Path) -> None:
        """Comprueba que un directorio ya existente se reutiliza sin error."""
        target = tmp_path / "out"
        target.mkdir()

        assert _process_output_directory(target) == target

    def test_creation_failure_raises_user_error(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Comprueba que un fallo al crear el directorio se informa al usuario."""

        def _refuse(*_args: object, **_kwargs: object) -> None:
            """Simula un sistema de ficheros sin permiso de escritura."""
            raise PermissionError

        monkeypatch.setattr(Path, "mkdir", _refuse)

        with pytest.raises(UserError, match="Could not create directory"):
            _process_output_directory(tmp_path / "denied")


class TestProcessOutput:
    """Pruebas del procesamiento de la ruta de salida (función compartida)."""

    def test_default_path_uses_media_name(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Comprueba que la salida por defecto usa el nombre de la media."""
        monkeypatch.chdir(tmp_path)

        output = _process_output(
            _media_with_path(),
            extension=".gif",
        )

        assert output == (tmp_path / "clip.gif").absolute()

    def test_affix_and_extension_applied(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Comprueba que se aplican el sufijo y la extensión indicados."""
        monkeypatch.chdir(tmp_path)

        output = _process_output(
            _media_with_path(),
            extension=".gif",
            affix="_edit",
        )

        assert output == (tmp_path / "clip_edit.gif").absolute()

    def test_explicit_output_ignores_affix(self, tmp_path: Path) -> None:
        """Comprueba que una ruta explícita no aplica el sufijo."""
        explicit = tmp_path / "done.gif"

        output = _process_output(
            _media_with_path(),
            extension=".gif",
            affix="_x",
            output=explicit,
        )

        assert output == (tmp_path / "done.gif").absolute()

    def test_output_directory_used_as_parent(self, tmp_path: Path) -> None:
        """Comprueba que el directorio es el padre de la salida por defecto."""
        target = tmp_path / "out"

        output = _process_output(
            _media_with_path(),
            extension=".gif",
            output_directory=target,
        )

        assert output == (target / "clip.gif").absolute()

    def test_output_without_extension_keeps_explicit_name(self, tmp_path: Path) -> None:
        """Comprueba que una extensión vacía no modifica la ruta explícita."""
        explicit = tmp_path / "noext"

        output = _process_output(_media_with_path(), extension="", output=explicit)

        assert output == explicit.absolute()

    @pytest.mark.parametrize("name", ["bad<name>.mp4", "bad?name.mp4", "con.mp4"])
    def test_output_name_with_invalid_characters_is_rejected(
        self, tmp_path: Path, name: str
    ) -> None:
        """Comprueba que un nombre de salida no válido se rechaza."""
        with pytest.raises(UserError, match="contains invalid characters"):
            _process_output(
                _media_with_path(), extension=".mp4", output=tmp_path / name
            )

    def test_output_equal_to_the_input_is_rejected(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Comprueba que la salida no puede coincidir con la entrada."""
        monkeypatch.chdir(tmp_path)
        media = _media_with_path()

        with pytest.raises(UserError, match="must be different"):
            _process_output(media, extension=".mp4", output=media.path.absolute())

    def test_tilde_and_env_vars_are_not_expanded(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Comprueba que `~` y las variables de entorno quedan literales."""
        monkeypatch.chdir(tmp_path)

        output = _process_output(
            _media_with_path(), extension=".gif", output=Path("~/v$VAR/clip.gif")
        )

        assert output == (tmp_path / "~" / "v$VAR" / "clip.gif").absolute()


class TestMediaOutputMixin:
    """Pruebas del mixin de salida de contenedores multimedia."""

    def test_requires_video_track(self, tmp_path: Path) -> None:
        """Comprueba que la salida de vídeo exige una pista de vídeo."""
        mixin = _media_mixin(media=_media_with_path())

        with pytest.raises(MissingPropertyError, match="video"):
            mixin.create_media_output(extension=".mp4", output=tmp_path / "out.mp4")

    def test_requires_codec(self, tmp_path: Path) -> None:
        """Comprueba que la salida de vídeo exige un códec en la pista."""
        mixin = _media_mixin(media=_media_with_path(video=_video(None)))

        with pytest.raises(MissingPropertyError, match="video codec"):
            mixin.create_media_output(extension=".mp4", output=tmp_path / "out.mp4")

    def test_sets_media_output(self, tmp_path: Path) -> None:
        """Comprueba que se asigna la salida al campo tipado."""
        mixin = _media_mixin(media=_media_with_path(video=_video("h264")))

        mixin.create_media_output(extension=".mp4", output=tmp_path / "out.mp4")

        assert mixin.media_output == (tmp_path / "out.mp4").absolute()

    def test_extension_not_supported_by_codec(self, tmp_path: Path) -> None:
        """Comprueba que un códec que no soporta la extensión lanza un error."""
        mixin = _media_mixin(media=_media_with_path(video=_video("h264")))

        # .webm es un destino de vídeo soportado, pero no admite h264
        with pytest.raises(UserError) as exc_info:
            mixin.create_media_output(extension=".webm", output=tmp_path / "out.webm")

        assert "h264" in str(exc_info.value)

    def test_not_media_extension(self, tmp_path: Path) -> None:
        """Comprueba el error cuando la extensión no es contenedor de vídeo."""
        mixin = _media_mixin(media=_media_with_path(video=_video("h264")))

        with pytest.raises(UserError):
            mixin.create_media_output(extension=".mp4", output=tmp_path / "out.txt")

    def test_audio_codec_checked(self, tmp_path: Path) -> None:
        """Comprueba que el contenedor de vídeo también soporta los códecs de audio."""
        mixin = _media_mixin(
            media=_media_with_path(video=_video("h264"), audio=_audio("vorbis"))
        )

        # .mp4 es válido para h264 pero no para vorbis
        with pytest.raises(UserError) as exc_info:
            mixin.create_media_output(extension=".mp4", output=tmp_path / "out.mp4")

        assert "vorbis" in str(exc_info.value)

    def test_audio_codec_required(self, tmp_path: Path) -> None:
        """Comprueba que el contenedor de vídeo exige códec en cada pista."""
        mixin = _media_mixin(
            media=_media_with_path(video=_video("h264"), audio=_audio(None))
        )

        with pytest.raises(MissingPropertyError, match="audio codec"):
            mixin.create_media_output(extension=".mp4", output=tmp_path / "out.mp4")

    def test_output_equal_to_second_input_is_rejected(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Comprueba que la validación cubre todas las entradas del lote."""
        monkeypatch.chdir(tmp_path)
        first = _media_with_path("a.mp4", video=_video("h264"))
        second = _media_with_path("b.mp4", video=_video("h264"))
        mixin = _media_mixin(media=first)

        with pytest.raises(UserError, match="must be different"):
            mixin.create_media_output(
                extension=".mp4",
                output=Path("b.mp4"),
                media_list=[first, second],
            )


class TestValidateName:
    """Pruebas de validación de nombres de fichero."""

    @pytest.mark.parametrize("name", ["clip", "clip final", "Clip-01_v2", "vídeo ñ"])
    def test_valid_names_do_not_raise(self, name: str) -> None:
        """Comprueba que los nombres válidos no lanzan errores."""
        _validate_name(name)

    @pytest.mark.parametrize(
        "name",
        ["a<b", "a>b", "a:b", 'a"b', "a/b", "a\\b", "a|b", "a?b", "a*b", "a\x00b"],
    )
    def test_invalid_characters(self, name: str) -> None:
        """Comprueba que los caracteres no permitidos lanzan un error."""
        with pytest.raises(UserError):
            _validate_name(name)

    @pytest.mark.parametrize(
        "name", ["CON", "con", "PRN", "AUX", "NUL", "LPT1", "COM9"]
    )
    def test_reserved_names(self, name: str) -> None:
        """Comprueba que los nombres reservados de Windows lanzan un error."""
        with pytest.raises(UserError):
            _validate_name(name)

    @pytest.mark.parametrize("name", ["clip ", "clip."])
    def test_trailing_space_or_dot(self, name: str) -> None:
        """Comprueba que un espacio o punto final lanzan un error."""
        with pytest.raises(UserError):
            _validate_name(name)

    def test_empty_name(self) -> None:
        """Comprueba que un nombre vacío lanza un error."""
        with pytest.raises(UserError):
            _validate_name("")
