"""Tests de integridad del sistema gettext de pyMedia.

Valida la plantilla POT, los catálogos PO y los compilados MO:
- Existencia y validez sintáctica.
- Unicidad de msgid y msgstr no vacío.
- Paridad de placeholders `%(name)s` entre msgid y msgstr.
- Compilación en memoria sin error.
- Todo msgid del POT se usa en `src/`.
- Los locales disponibles en disco coinciden con los declarados.
- Todas las entradas del PO están compiladas en el `.mo`.
"""

import io
import re
from pathlib import Path

import pytest
from babel.messages.catalog import Catalog
from babel.messages.extract import extract_from_dir
from babel.messages.mofile import read_mo, write_mo
from babel.messages.pofile import read_po

pytestmark = pytest.mark.prod

_SRC_DIR = Path(__file__).resolve().parents[1] / "src"
_LOCALEDIR = _SRC_DIR / "pymedia" / "locales"
_DOMAIN = "pymedia"
_LANGUAGES = ["es"]


def _read_po(path: Path) -> Catalog:
    """Lee un archivo PO y devuelve el catálogo."""
    with path.open("rb") as f:
        return read_po(f)


def _pot_path() -> Path:
    return _LOCALEDIR / f"{_DOMAIN}.pot"


def _po_path(lang: str) -> Path:
    return _LOCALEDIR / lang / "LC_MESSAGES" / f"{_DOMAIN}.po"


def _placeholder_params(text: str) -> set[str]:
    """Extrae los nombres de placeholder `%(name)s` de un texto."""
    return set(re.findall(r"%\(\w+\)s", text))


def _mo_path(lang: str) -> Path:
    return _po_path(lang).with_suffix(".mo")


def _read_mo(path: Path) -> Catalog:
    """Lee un archivo MO y devuelve el catálogo."""
    with path.open("rb") as f:
        return read_mo(f)


def _entries(catalog: Catalog) -> dict[str, str]:
    """Devuelve {msgid: msgstr}, descartando el header y formas plurales."""
    entries: dict[str, str] = {}
    for message in catalog:
        if (
            isinstance(message.id, str)
            and message.id
            and isinstance(message.string, str)
        ):
            entries[message.id] = message.string
    return entries


def _available_languages() -> set[str]:
    """Devuelve los códigos de idioma con catálogo PO presente en disco."""
    return {
        path.parents[1].name for path in _LOCALEDIR.glob(f"*/LC_MESSAGES/{_DOMAIN}.po")
    }


# ─── 1) POT existe y es válido ────────────────────────────────────────────


def test_pot_exists() -> None:
    """La plantilla POT existe y contiene al menos un msgid."""
    pot = _pot_path()
    assert pot.exists(), f"Falta la plantilla: {pot}"
    catalog = _read_po(pot)
    assert len(catalog) > 0, "La plantilla POT está vacía"


# ─── 2) PO existe para cada idioma ────────────────────────────────────────


@pytest.mark.parametrize("lang", _LANGUAGES)
def test_po_exists(lang: str) -> None:
    """Existe un catálogo PO para cada idioma soportado."""
    po = _po_path(lang)
    assert po.exists(), f"Falta el catálogo: {po}"


# ─── 2b) Locales disponibles actualizados ─────────────────────────────────


def test_available_locales_updated() -> None:
    """Los catálogos en disco coinciden con los idiomas declarados."""
    disponibles = _available_languages()
    declarados = set(_LANGUAGES)

    assert disponibles == declarados, (
        f"Locales en disco ({sorted(disponibles)}) no coinciden con los "
        f"declarados ({sorted(declarados)}). Añade el catálogo o actualiza "
        "`_LANGUAGES`."
    )

    for lang in declarados:
        mo = _mo_path(lang)
        assert mo.exists(), (
            f"Falta el compilado para `{lang}`: {mo} (ejecuta `compile -l {lang}`)"
        )


# ─── 3) Unicidad y msgstr no vacío ───────────────────────────────────────


@pytest.mark.parametrize("lang", _LANGUAGES)
def test_msgids_unique_and_translated(lang: str) -> None:
    """Los msgid son únicos y todo msgstr no vacío (salvo el header)."""
    catalog = _read_po(_po_path(lang))
    seen: set[str] = set()
    errores: list[str] = []

    for message in catalog:
        msgid = message.id
        if not isinstance(msgid, str) or not msgid:
            continue  # header o formas plurales del PO
        if msgid in seen:
            errores.append(f"msgid duplicado: {msgid!r}")
        seen.add(msgid)
        msgstr = message.string
        if not isinstance(msgstr, str) or not msgstr:
            errores.append(f"msgstr vacío: {msgid!r}")

    assert not errores, "\n".join(errores)


# ─── 4) Paridad de placeholders ───────────────────────────────────────────


@pytest.mark.parametrize("lang", _LANGUAGES)
def test_placeholder_parity(lang: str) -> None:
    """Msgid y msgstr tienen los mismos placeholders `%(name)s`."""
    catalog = _read_po(_po_path(lang))
    errores: list[str] = []

    for message in catalog:
        msgid = message.id
        msgstr = message.string
        if not isinstance(msgid, str) or not isinstance(msgstr, str):
            continue
        if not msgid or not msgstr:
            continue
        if _placeholder_params(msgid) != _placeholder_params(msgstr):
            errores.append(f"placeholders distintos: {msgid!r} vs {msgstr!r}")

    assert not errores, "\n".join(errores)


# ─── 5) Compilación en memoria ────────────────────────────────────────────


@pytest.mark.parametrize("lang", _LANGUAGES)
def test_catalog_compiles_in_memory(lang: str) -> None:
    """El catálogo PO compila a MO sin errores."""
    catalog = _read_po(_po_path(lang))
    stream = io.BytesIO()
    write_mo(stream, catalog)
    assert stream.tell() > 0, "El MO generado está vacío"


# ─── 6) PO totalmente compilado ──────────────────────────────────────────


@pytest.mark.parametrize("lang", _LANGUAGES)
def test_po_fully_compiled(lang: str) -> None:
    """Todas las entradas del PO están compiladas y al día en el MO."""
    mo = _mo_path(lang)
    assert mo.exists(), f"Falta el compilado: {mo} (ejecuta `compile -l {lang}`)"

    po_entries = _entries(_read_po(_po_path(lang)))
    mo_entries = _entries(_read_mo(mo))

    sin_compilar = sorted(set(po_entries) - set(mo_entries))
    desactualizadas = sorted(
        msgid
        for msgid, msgstr in po_entries.items()
        if msgid in mo_entries and mo_entries[msgid] != msgstr
    )

    assert not sin_compilar, "Entradas del PO sin compilar en el MO:\n" + "\n".join(
        sin_compilar
    )
    assert not desactualizadas, (
        "Entradas del PO con msgstr distinta al MO (recompila):\n"
        + "\n".join(desactualizadas)
    )


# ─── 7) Todo msgid del POT se usa en src/ ────────────────────────────────


def test_all_pot_msgids_used_in_src() -> None:
    """Cada msgid del POT aparece en el código fuente de `src/`."""
    pot = _read_po(_pot_path())
    extraido = Catalog(domain=_DOMAIN)
    for filename, lineno, message, _comments, context in extract_from_dir(
        str(_SRC_DIR),
        keywords={"_": None, "ngettext": (1, 2)},
        directory_filter=lambda d: Path(d).name != "locales",
    ):
        if message is None or context is not None:
            continue
        extraido.add(message, locations=[(filename, lineno)])

    faltan = [
        m.id for m in pot if isinstance(m.id, str) and m.id and m.id not in extraido
    ]
    assert not faltan, "msgids en POT no usados en src/:\n" + "\n".join(faltan)
