"""Tests para los mixins de entrada (pymedia.models.mixins.inputs_mixin)."""

from pathlib import Path

import pytest

from pymedia.errors import (
    InvalidContainerTypeError,
    MissingParameterError,
)
from pymedia.models.media import Media
from pymedia.models.mixins.inputs_mixin import MediaListMixin, MediaMixin

_EMPTY_METADATA = {"streams": [], "format": {}}


@pytest.fixture(autouse=True)
def _fake_probe(monkeypatch):
    """Evita ejecutar ffprobe en todos los tests de este módulo."""
    monkeypatch.setattr(
        "pymedia.models.mixins.inputs_mixin.get_media_metadata",
        lambda path, logger: _EMPTY_METADATA,
    )


def _media(path: Path) -> Media:
    """Media con la ruta indicada y sin metadatos."""
    return Media(path=path)


class TestInputSingleCreate:
    """Pruebas de creación de la entrada individual."""

    def test_sets_media_with_absolute_path(self, tmp_path, monkeypatch):
        """Comprueba que se guardan la ruta absoluta y los metadatos."""
        monkeypatch.chdir(tmp_path)
        mixin = MediaMixin()
        source = Path("clip.mp4")

        mixin.create_media_input(media_input=source, logger=None)

        assert mixin.media == _media(source.absolute())

    def test_invalid_extension_raises(self, tmp_path):
        """Comprueba que una extensión no de vídeo lanza un error."""
        mixin = MediaMixin()

        with pytest.raises(InvalidContainerTypeError):
            mixin.create_media_input(media_input=tmp_path / "clip.txt", logger=None)


class TestInputSingleCmd:
    """Pruebas de generación del comando de entrada individual."""

    def test_to_media_input_cmd(self):
        """Comprueba que se genera el argumento `-i` correctamente."""
        source = Path("clip.mp4")
        mixin = MediaMixin(media=_media(source))

        assert mixin.to_media_input_cmd() == ["-i", str(source)]

    def test_to_media_input_cmd_missing_parameter(self):
        """Comprueba que falta lanzar un error si no hay media."""
        mixin = MediaMixin()

        with pytest.raises(MissingParameterError, match="media"):
            mixin.to_media_input_cmd()


class TestInputListCreate:
    """Pruebas de creación de la lista de entradas."""

    def test_creates_media_list(self, tmp_path, monkeypatch):
        """Comprueba que se guardan rutas absolutas y sus metadatos."""
        monkeypatch.chdir(tmp_path)
        mixin = MediaListMixin()
        source_a = Path("a.mp4")
        source_b = Path("b.mp4")

        mixin.create_media_list(media_input_list=[source_a, source_b], logger=None)

        assert mixin.media_list == [
            Media(path=source_a.absolute()),
            Media(path=source_b.absolute()),
        ]

    def test_invalid_extension_raises(self, tmp_path):
        """Comprueba que una extensión no de vídeo lanza un error."""
        mixin = MediaListMixin()

        with pytest.raises(InvalidContainerTypeError):
            mixin.create_media_list(media_input_list=[tmp_path / "x.txt"], logger=None)

    def test_load_failure_raises_missing_media(self, monkeypatch):
        """Comprueba que un fallo de ffprobe lanza un error."""
        import subprocess

        def _failing_probe(path, logger):
            raise subprocess.CalledProcessError(1, ["ffprobe"])

        monkeypatch.setattr(
            "pymedia.models.mixins.inputs_mixin.get_media_metadata", _failing_probe
        )
        mixin = MediaListMixin()

        with pytest.raises(subprocess.CalledProcessError):
            mixin.create_media_list(media_input_list=[Path("x.mp4")], logger=None)


class TestInputListCmd:
    """Pruebas de generación del comando de lista de entradas."""

    def test_to_media_input_list_cmd(self):
        """Comprueba que se genera un `-i` por cada entrada."""
        mixin = MediaListMixin(
            media_list=[Media(path=Path("a.mp4")), Media(path=Path("b.mp4"))]
        )

        assert mixin.to_media_input_list_cmd() == ["-i", "a.mp4", "-i", "b.mp4"]

    def test_to_media_input_list_cmd_missing_parameter(self):
        """Comprueba que falta lanzar un error si no hay lista."""
        mixin = MediaListMixin()

        with pytest.raises(MissingParameterError, match="media_list"):
            mixin.to_media_input_list_cmd()
