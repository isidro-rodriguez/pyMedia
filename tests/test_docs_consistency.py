"""Contraste entre la CLI real, la documentación, el README y la página de manual.

Las opciones se leen de la aplicación Typer construida, así que un comando o una
opción nuevos, renombrados o retirados obligan a actualizar la documentación.
"""

import re
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Protocol

import pytest
import typer
from typer.core import TyperGroup

from pymedia.main import _build_app

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "usuario"
COMMANDS_DOCS = DOCS / "comandos"
CONCEPTS = DOCS / "conceptos.md"
FILTERS_DOC = "filtros.md"
MAN_PAGE = ROOT / "src" / "pymedia" / "resources" / "pymedia.1"
README = ROOT / "README.md"

FILTER_OPTIONS = frozenset(
    {"--crop", "--size", "--mode", "--upscale", "--rotate", "--hflip", "--vflip"}
)
"""Filtros de imagen: se documentan en `filtros.md` y se enlazan desde el comando."""

FOREIGN_OPTIONS = frozenset({"--force"})
"""Opciones de otras herramientas citadas en la documentación (`uv tool --force`)."""


class _Command(Protocol):
    """Comando de Click (integrado en Typer): solo interesan sus parámetros."""

    @property
    def params(self) -> Sequence[Any]:
        """Opciones y argumentos del comando."""
        ...


_GROUP = typer.main.get_command(_build_app())
assert isinstance(_GROUP, TyperGroup)
COMMANDS = dict(_GROUP.commands)
NAMES = sorted(COMMANDS)


def _options(command: _Command, *, negatives: bool = True) -> set[str]:
    """Opciones de un comando, con o sin las formas `--no-…`."""
    options: set[str] = set()
    for param in command.params:
        flags = param.opts + (param.secondary_opts if negatives else [])
        options.update(flag for flag in flags if flag.startswith("-"))
    return options


def _sections() -> dict[str, str]:
    """Texto de cada sección `## comando` junto con la introducción de su página."""
    sections: dict[str, str] = {}
    for page in sorted(COMMANDS_DOCS.glob("*.md")):
        parts = re.split(
            r"^## `([\w-]+)`\s*$", page.read_text(encoding="utf-8"), flags=re.M
        )
        intro = parts[0]
        for name, body in zip(parts[1::2], parts[2::2], strict=True):
            sections[name] = intro + body
    return sections


def _common_options() -> dict[tuple[str, ...], str]:
    """Filas de «Opciones comunes» en `conceptos.md`: opciones → disponibilidad."""
    text = CONCEPTS.read_text(encoding="utf-8")
    table = text.split("## Opciones comunes", 1)[1].split("\n\n", 2)[1]
    rows: dict[tuple[str, ...], str] = {}
    for line in table.splitlines()[2:]:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        rows[tuple(re.findall(r"`(-[\w-]+)`", cells[0]))] = cells[1]
    return rows


def _declared_commands(availability: str) -> set[str]:
    """Interpreta «Todos», «Todos salvo `x`» o una lista de comandos."""
    named = set(re.findall(r"`([\w-]+)`", availability))
    if availability.startswith("Todos salvo"):
        return set(NAMES) - named
    if availability.startswith("Todos"):
        return set(NAMES)
    return named


SECTIONS = _sections()
COMMON = _common_options()
COMMON_FLAGS = frozenset(flag for flags in COMMON for flag in flags)


# =============================================================================
#  Comandos
# =============================================================================


@pytest.mark.parametrize("name", NAMES)
def test_command_has_docs_section(name: str) -> None:
    """Cada comando tiene su sección `## nombre` en `docs/usuario/comandos/`."""
    assert name in SECTIONS


@pytest.mark.parametrize("name", NAMES)
def test_command_in_man_page(name: str) -> None:
    """Cada comando aparece como entrada `.B nombre` en la página de manual."""
    assert re.search(
        rf"^\.B {re.escape(name)}$", MAN_PAGE.read_text(encoding="utf-8"), re.M
    )


@pytest.mark.parametrize("name", NAMES)
def test_command_in_readme(name: str) -> None:
    """Cada comando tiene una fila en la tabla de uso del README."""
    assert f"| `{name}` " in README.read_text(encoding="utf-8")


def test_docs_do_not_describe_missing_commands() -> None:
    """No se documentan comandos que ya no existen."""
    assert set(SECTIONS) <= set(NAMES)


# =============================================================================
#  Opciones
# =============================================================================


@pytest.mark.parametrize("name", NAMES)
def test_command_options_documented(name: str) -> None:
    """Las opciones propias del comando aparecen en su sección.

    Las comunes se documentan en `conceptos.md` y los filtros en `filtros.md`,
    que la sección (o la introducción de su página) debe enlazar.
    """
    section = SECTIONS[name]
    options = _options(COMMANDS[name], negatives=False) - COMMON_FLAGS
    if options & FILTER_OPTIONS and FILTERS_DOC in section:
        options -= FILTER_OPTIONS

    missing = sorted(
        option
        for option in options
        if not re.search(rf"`{re.escape(option)}(?![\w-])", section)
    )
    assert not missing, f"{name}: sin documentar {missing}"


@pytest.mark.parametrize("flags", list(COMMON), ids=" ".join)
def test_common_options_availability(flags: tuple[str, ...]) -> None:
    """La columna «Disponible en» de cada opción común coincide con la CLI."""
    actual = {
        name for name, command in COMMANDS.items() if set(flags) & _options(command)
    }
    assert _declared_commands(COMMON[flags]) == actual


@pytest.mark.parametrize("name", NAMES)
def test_command_options_in_man_page(name: str) -> None:
    """Todas las opciones del comando aparecen en la página de manual."""
    man = MAN_PAGE.read_text(encoding="utf-8")
    missing = sorted(
        option
        for option in _options(COMMANDS[name], negatives=False)
        if not re.search(rf"(?<![\w-]){re.escape(option)}(?![\w-])", man)
    )
    assert not missing, f"{name}: falta en pymedia.1 {missing}"


def test_docs_do_not_mention_missing_options() -> None:
    """Ninguna opción citada en la documentación, README o manual está retirada."""
    known = {option for command in COMMANDS.values() for option in _options(command)}
    known |= _options(_GROUP) | FOREIGN_OPTIONS
    sources = [*DOCS.rglob("*.md"), README, MAN_PAGE]

    stale = sorted(
        {
            f"{option} ({source.name})"
            for source in sources
            for option in re.findall(
                r"(?<![\w-])(--[a-z][a-z0-9-]*[a-z0-9])(?![\w-])",
                source.read_text(encoding="utf-8"),
            )
            if option not in known
        }
    )
    assert not stale, f"Opciones inexistentes: {stale}"
