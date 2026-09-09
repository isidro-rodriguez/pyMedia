"""Tests de coherencia entre el catálogo de contenedores y los de códecs."""

from pymedia.data.audio_codecs import AUDIO_CODECS
from pymedia.data.containers import (
    AUDIO_CONTAINERS,
    CONTAINERS,
    SUBTITLES_CONTAINERS,
    VIDEO_CONTAINERS,
)
from pymedia.data.subtitles_formats import SUBTITLES_FORMATS
from pymedia.data.video_codecs import VIDEO_CODECS

# ---------------------------------------------------------------- catálogo


def test_container_extensions_are_unique():
    """Las extensiones de contenedor no se repiten."""
    extensions = [container.extension for container in CONTAINERS.values()]

    assert len(extensions) == len(set(extensions))


def test_container_names_are_unique():
    """Los nombres de contenedor no se repiten."""
    names = [container.name for container in CONTAINERS.values()]

    assert len(names) == len(set(names))


def test_extension_format():
    """Las extensiones llevan punto y están en minúsculas."""
    for container in CONTAINERS.values():
        assert container.extension.startswith("."), container.extension
        assert container.extension.islower(), container.extension


def test_mime_type_is_present():
    """Todos los contenedores tienen tipo MIME."""
    for container in CONTAINERS.values():
        assert container.mime_type, f"{container.extension} sin mime_type"


# ------------------------------------------------- códecs conocidos


def test_video_codecs_are_known():
    """Los códecs de vídeo de cada contenedor existen en VIDEO_CODECS."""
    for container in CONTAINERS.values():
        unknown = set(container.video_codecs) - set(VIDEO_CODECS)
        msg = f"{container.extension}: códecs de vídeo desconocidos {unknown}"

        assert not unknown, msg


def test_audio_codecs_are_known():
    """Los códecs de audio de cada contenedor existen en AUDIO_CODECS."""
    for container in CONTAINERS.values():
        unknown = set(container.audio_codecs) - set(AUDIO_CODECS)
        msg = f"{container.extension}: códecs de audio desconocidos {unknown}"

        assert not unknown, msg


def test_subtitles_codecs_are_known():
    """Los códecs de subtítulos de cada contenedor existen en SUBTITLES_FORMATS."""
    for container in CONTAINERS.values():
        unknown = set(container.subtitles_codecs) - set(SUBTITLES_FORMATS)
        msg = f"{container.extension}: códecs de subtítulo desconocidos {unknown}"

        assert not unknown, msg


# ------------------------------------------------------- sin huérfanos


def test_no_orphan_codec_containers():
    """Toda extensión referenciada por un códec tiene contenedor."""
    referenced: set[str] = set()
    for codec in VIDEO_CODECS.values():
        referenced.update(codec.containers)
    for codec in AUDIO_CODECS.values():
        referenced.update(codec.containers)
    for codec in SUBTITLES_FORMATS.values():
        referenced.update(codec.containers)

    orphans = referenced - set(CONTAINERS)

    assert not orphans, f"Extensiones de códecs sin contenedor: {sorted(orphans)}"


def test_all_codecs_have_containers():
    """Ningún códec del catálogo tiene la lista de contenedores vacía."""
    for catalog in (VIDEO_CODECS, AUDIO_CODECS, SUBTITLES_FORMATS):
        for name, codec in catalog.items():
            assert codec.containers, f"El códec '{name}' no tiene contenedores"


# -------------------------------------------------- mapeo bidireccional


def test_video_codec_mapping_is_bidirectional():
    """Cada códec de vídeo de un contenedor lo lista en sus containers."""
    for container in CONTAINERS.values():
        for codec_name in container.video_codecs:
            assert container.extension in VIDEO_CODECS[codec_name].containers, (
                f"{container.extension} no aparece en {codec_name}.containers"
            )


def test_audio_codec_mapping_is_bidirectional():
    """Cada códec de audio de un contenedor lo lista en sus containers."""
    for container in CONTAINERS.values():
        for codec_name in container.audio_codecs:
            assert container.extension in AUDIO_CODECS[codec_name].containers, (
                f"{container.extension} no aparece en {codec_name}.containers"
            )


def test_subtitles_mapping_is_bidirectional():
    """Cada códec de subtítulo de un contenedor lo lista en sus containers."""
    for container in CONTAINERS.values():
        for codec_name in container.subtitles_codecs:
            assert container.extension in SUBTITLES_FORMATS[codec_name].containers, (
                f"{container.extension} no aparece en {codec_name}.containers"
            )


def test_remux_containers_subset_of_containers():
    """Los destinos de remux seguro son subconjunto de los contenedores válidos."""
    catalogos = (VIDEO_CODECS, AUDIO_CODECS, SUBTITLES_FORMATS)

    for catalogo in catalogos:
        for codec_name, codec_data in catalogo.items():
            assert set(codec_data.remux_containers) <= set(codec_data.containers), (
                f"{codec_name}: {codec_data.remux_containers} no es subconjunto "
                f"de {codec_data.containers}"
            )


# ------------------------------------------------ tuplas derivadas


def test_derived_video_containers_match_catalog():
    """VIDEO_CONTAINERS se deriva del catálogo de contenedores."""
    expected = tuple(
        container.extension
        for container in CONTAINERS.values()
        if container.video_codecs
    )

    assert VIDEO_CONTAINERS == expected


def test_derived_audio_containers_match_catalog():
    """AUDIO_CONTAINERS se deriva del catálogo de contenedores."""
    expected = tuple(
        container.extension
        for container in CONTAINERS.values()
        if container.audio_codecs
    )

    assert AUDIO_CONTAINERS == expected


def test_derived_subtitles_containers_match_catalog():
    """SUBTITLES_CONTAINERS se deriva del catálogo de contenedores."""
    expected = tuple(
        container.extension
        for container in CONTAINERS.values()
        if container.subtitles_codecs
    )

    assert SUBTITLES_CONTAINERS == expected
