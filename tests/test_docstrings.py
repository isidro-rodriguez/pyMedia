"""Sincronía entre los docstrings de las dataclasses de pipeline y sus campos.

Las dataclasses *Arguments/*Parameters re-documentan en su sección
`Attributes:` los campos heredados de los mixins (resumen de IDE).
Este test garantiza que esa duplicación no deriva: cada nombre
documentado debe existir como campo real, y viceversa.
"""

import dataclasses
import re

import pytest
from pymedia.models.pipeline.gif_pipeline import GifArguments, GifParameters
from pymedia.models.pipeline.info_pipeline import InfoArguments, InfoParameters
from pymedia.models.pipeline.sheet_pipeline import SheetArguments, SheetParameters

from pymedia.typer.commands.thumbnail_pipeline import (
    ScreenshootParameters,
    ThumbnailArguments,
)

SECTION_HEADER = re.compile(r"^\s*(Args|Returns|Raises|Examples?|Notes?|Warns)\s*:\s*$")
ATTR_ITEM = re.compile(r"^\s+\*{0,2}([a-z][a-z0-9_]*)\s*(?:\(.+?\))?\s*:")

PIPELINE_DATACLASSES = [
    GifArguments,
    GifParameters,
    InfoArguments,
    InfoParameters,
    SheetArguments,
    SheetParameters,
    ThumbnailArguments,
    ScreenshootParameters,
]


def _documented_attributes(cls: type) -> set[str]:
    """Extrae los nombres listados en la sección `Attributes:` del docstring.

    Args:
        cls: Dataclass cuyo docstring se analiza.

    Returns:
        Nombres documentados; vacío si la sección no existe.
    """
    doc = cls.__doc__ or ""
    lines = doc.splitlines()
    documented: set[str] = set()
    in_attributes = False
    for line in lines:
        if line.strip() == "Attributes:":
            in_attributes = True
            continue
        if in_attributes:
            if SECTION_HEADER.match(line) or not line.strip():
                if SECTION_HEADER.match(line):
                    in_attributes = False
                continue
            item = ATTR_ITEM.match(line)
            if item is not None:
                documented.add(item.group(1))
    return documented


def _actual_fields(cls: type) -> set[str]:
    """Devuelve los nombres de los campos reales de la dataclass.

    Args:
        cls: Dataclass a inspeccionar.

    Returns:
        Nombres de todos los campos, incluidos los heredados de mixins.
    """
    return {field.name for field in dataclasses.fields(cls)}  # type: ignore[arg-type]


@pytest.mark.parametrize("cls", PIPELINE_DATACLASSES, ids=lambda cls: cls.__name__)
def test_attributes_in_sync_with_fields(cls: type) -> None:
    """Los atributos documentados coinciden con los campos reales de la dataclass."""
    documented = _documented_attributes(cls)
    actual = _actual_fields(cls)

    orphaned = sorted(documented - actual)
    missing = sorted(actual - documented)

    assert not orphaned, (
        f"{cls.__name__}: atributos documentados que no existen: {orphaned}"
    )
    assert not missing, (
        f"{cls.__name__}: campos sin documentar en Attributes: {missing}"
    )
