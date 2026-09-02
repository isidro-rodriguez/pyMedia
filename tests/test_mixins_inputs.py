"""Tests para los mixins de entrada (pymedia.models.mixins.inputs_mixin)."""

from pathlib import Path

import pytest

from pymedia.errors import (
    InvalidContainerTypeError,
    MissingMediaError,
    MissingParameterError,
)
from pymedia.models.media import Media
from pymedia.models.mixins.inputs_mixin import InputListMixin, InputSingleMixin


def _fake_load_returns_media(path, logger) -> Media:
    """Stub de Media.load: devuelve una Media vacía sin tocar ffprobe."""
    return Media()


def _fake_load_raises(path, logger) -> Media:
    """Stub de Media.load: simula un fallo de ffprobe."""
    raise ValueError("probe failed")


@pytest.fixture(autouse=True)
def _fake_probe(monkeypatch):
    """Evita ejecutar ffprobe en todos los tests de este módulo."""
    monkeypatch.setattr(
        "pymedia.models.mixins.inputs_mixin.Media.load", _fake_load_returns_media
    )


class TestInputSingleCreate:
    """Pruebas de creación de la entrada individual."""

    def test_sets_absolute_path_and_media(self, tmp_path, monkeypatch):
        """Comprueba que se guardan la ruta absoluta y los metadatos."""
        monkeypatch.chdir(tmp_path)
        mixin = InputSingleMixin()
        source = tmp_path / "clip.mp4"

        mixin.create_input_single(input_single=source, logger=None)

        assert mixin.input_single == source.absolute()
        assert mixin.media == Media()

    def test_invalid_extension_raises(self, tmp_path):
        """Comprueba que una extensión no de vídeo lanza un error."""
        mixin = InputSingleMixin()

        with pytest.raises(InvalidContainerTypeError) as exc_info:
            mixin.create_input_single(input_single=tmp_path / "clip.txt", logger=None)

        assert "Video" in exc_info.value.message

    def test_converts_to_absolute_path(self, tmp_path, monkeypatch):
        """Comprueba que una ruta relativa se convierte en absoluta."""
        monkeypatch.chdir(tmp_path)
        mixin = InputSingleMixin()
        relative = Path("clip.mp4")

        mixin.create_input_single(input_single=relative, logger=None)

        assert mixin.input_single == relative.absolute()


class TestInputSingleCmd:
    """Pruebas de generación del comando de entrada individual."""

    def test_to_input_single_cmd(self):
        """Comprueba que se genera el argumento `-i` correctamente."""
        source = Path("clip.mp4")
        mixin = InputSingleMixin(input_single=source)

        assert mixin.to_input_single_cmd() == ["-i", str(source)]

    def test_to_input_single_cmd_missing_parameter(self):
        """Comprueba que falta lanzar un error si no hay ruta."""
        mixin = InputSingleMixin()

        with pytest.raises(MissingParameterError, match="input_single"):
            mixin.to_input_single_cmd()


class TestInputListCreate:
    """Pruebas de creación de la lista de entradas."""

    def test_creates_absolute_paths_and_media(self, tmp_path, monkeypatch):
        """Comprueba que se guardan rutas absolutas y sus metadatos."""
        monkeypatch.chdir(tmp_path)
        mixin = InputListMixin()
        source_a = Path("a.mp4")
        source_b = Path("b.mp4")

        mixin.create_input_list(input_list=[source_a, source_b], logger=None)

        assert mixin.input_list == [source_a.absolute(), source_b.absolute()]
        assert mixin.media_list == [Media(), Media()]

    def test_replaces_existing_entries(self, tmp_path, monkeypatch):
        """Comprueba que una nueva lista reemplaza los valores previos."""
        monkeypatch.chdir(tmp_path)
        previous = Path("prev.mp4").absolute()
        mixin = InputListMixin(input_list=[previous], media_list=[Media()])

        mixin.create_input_list(input_list=[Path("new.mp4")], logger=None)

        assert mixin.input_list == [Path("new.mp4").absolute()]
        assert mixin.media_list == [Media()]

    def test_transactional_on_load_failure(self, monkeypatch):
        """Comprueba que un fallo de carga no deja estado a medio llenar."""
        calls = 0

        def _flaky_load(path, logger):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise ValueError("probe failed")
            return Media()

        monkeypatch.setattr(
            "pymedia.models.mixins.inputs_mixin.Media.load", _flaky_load
        )
        mixin = InputListMixin()

        with pytest.raises(MissingMediaError):
            mixin.create_input_list(
                input_list=[Path("a.mp4"), Path("b.mp4")], logger=None
            )

        # La carga falló a mitad: el estado no queda a medio llenar.
        assert mixin.input_list is None
        assert mixin.media_list is None


class TestInputListCmd:
    """Pruebas de generación del comando de lista de entradas."""

    def test_to_input_list_cmd(self):
        """Comprueba que se genera un `-i` por cada entrada."""
        mixin = InputListMixin(input_list=[Path("a.mp4"), Path("b.mp4")])

        assert mixin.to_input_list_cmd() == ["-i", "a.mp4", "-i", "b.mp4"]

    def test_to_input_list_cmd_missing_parameter(self):
        """Comprueba que falta lanzar un error si no hay lista."""
        mixin = InputListMixin()

        with pytest.raises(MissingParameterError, match="input_list"):
            mixin.to_input_list_cmd()


class TestLoadMedia:
    """Pruebas de la carga de metadatos de un medio."""

    def test_invalid_extension_raises(self):
        """Comprueba que una extensión no válida lanza un error."""
        with pytest.raises(InvalidContainerTypeError):
            InputListMixin(input_list=[], media_list=[]).create_input_list(
                input_list=[Path("x.txt")], logger=None
            )

    def test_load_error_raises_missing_media(self, monkeypatch):
        """Comprueba que un fallo de ffprobe lanza MissingMediaError."""
        monkeypatch.setattr(
            "pymedia.models.mixins.inputs_mixin.Media.load", _fake_load_raises
        )

        with pytest.raises(MissingMediaError) as exc_info:
            InputListMixin(input_list=[], media_list=[]).create_input_list(
                input_list=[Path("x.mp4")], logger=None
            )

        assert "x.mp4" in exc_info.value.message
