"""Tests de integridad del sistema de locales.

El local base es `en`. Se valida tanto el propio base (estructura, valores y
formato de plantillas) como el conjunto de locales (paridad entre idiomas y
uso de cada llave en el código fuente).

Los módulos de idioma se cargan aislados del paquete `pymedia` para no
disparar la detección de idioma global ni depender del entorno.
"""

import importlib.util
import re
from pathlib import Path
from string import Formatter
from typing import Any

import pytest

BASE_LOCALE = "en"

# Categorías expuestas por `pymedia.locales` vía `locale_service.set_language()`.
CATEGORIES = (
    "Cli",
    "Debug",
    "Info",
    "Progress",
    "ConfigValidation",
    "ExecutionError",
    "ParameterError",
    "ValidationError",
    "Warnings",
)

_PACKAGE_DIR = Path(__file__).resolve().parents[1] / "src" / "pymedia" / "locales"
_SRC_DIR = Path(__file__).resolve().parents[1] / "src"


def _load_locale(lang: str) -> Any:
    """Carga un módulo de idioma desde su archivo, sin tocar el paquete."""
    spec = importlib.util.spec_from_file_location(
        f"pymedia.locales.{lang}", _PACKAGE_DIR / f"{lang}.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _available_locales() -> list[str]:
    """Devuelve los nombres de los idiomas definidos en el paquete de locales."""
    return sorted(p.stem for p in _PACKAGE_DIR.glob("*.py") if p.name != "__init__.py")


def _non_base_locales() -> list[str]:
    """Idiomas distintos del base, para el test de paridad."""
    return [lang for lang in _available_locales() if lang != BASE_LOCALE]


# Sentinela usada para que el test de paridad se ejecute (y quede visible)
# aunque hoy solo exista el local base.
_FALLBACK_NO_NON_BASE = "<sin_locales_alternos>"


def _parameters(template: str) -> set[str]:
    """Extrae los nombres de parámetros de una plantilla de `str.format`."""
    return {name for _, name, _, _ in Formatter().parse(template) if name}


def _base_entries() -> list[tuple[str, str, str]]:
    """Lista (categoría, llave, valor) del local base."""
    base = _load_locale(BASE_LOCALE)
    return [
        (category, key, value)
        for category in CATEGORIES
        for key, value in getattr(base, category).items()
    ]


def _entry_ids(entries: list[tuple[str, str, str]]) -> list[str]:
    """IDs legibles `Categoria["llave"]` para parametrizar por cada entrada."""
    return [f'{category}["{key}"]' for category, key, _ in entries]


# ─── 1) Estructura ───────────────────────────────────────────────────────


@pytest.mark.parametrize("locale", _available_locales() or ["<sin_locales>"])
def test_estructura_categorias(lang: str) -> None:
    """Todo idioma define las categorías del contrato como dicts no vacíos."""
    if lang == "<sin_locales>":
        pytest.skip("No hay módulos de idioma definidos")

    module = _load_locale(lang)
    errores = []
    for category in CATEGORIES:
        if not hasattr(module, category):
            errores.append(f"{lang}: falta la categoría {category!r}")
            continue
        value = getattr(module, category)
        if not isinstance(value, dict):
            errores.append(f"{lang}.{category}: no es un dict")
        elif not value:
            errores.append(f"{lang}.{category}: está vacío")
    assert not errores, "\n".join(errores)


# ─── 2) Valores sanos (solo local base) ──────────────────────────────────


@pytest.mark.parametrize(
    "category,key,value", _base_entries(), ids=_entry_ids(_base_entries())
)
def test_valores_no_vacios(category: str, key: str, value: str) -> None:
    """Todo valor del local base es una cadena no vacía."""
    assert isinstance(value, str), f"{category}[{key}]: no es str"
    assert value.strip(), f"{category}[{key}]: valor vacío"


# ─── 3) Formato de plantillas (solo local base) ──────────────────────────


@pytest.mark.parametrize(
    "category,key,value", _base_entries(), ids=_entry_ids(_base_entries())
)
def test_formato_balanceado(category: str, key: str, value: str) -> None:
    """Las llaves de la plantilla están balanceadas (sin llaves huérfanas)."""
    try:
        list(Formatter().parse(value))
    except ValueError as exc:
        pytest.fail(f"{category}[{key}]: llaves desbalanceadas: {exc}")


@pytest.mark.parametrize(
    "category,key,value", _base_entries(), ids=_entry_ids(_base_entries())
)
def test_formato_aplica_parametros(category: str, key: str, value: str) -> None:
    """La plantilla se puede formatear rellenando sus parámetros con dummy."""
    params = _parameters(value)
    kwargs = {name: "x" for name in params}
    try:
        value.format(**kwargs)
    except (KeyError, IndexError, ValueError) as exc:
        pytest.fail(f"{category}[{key}]: no formatea con sus parámetros: {exc}")


# ─── 4) Paridad entre locales ────────────────────────────────────────────


@pytest.mark.parametrize(
    "locale",
    _non_base_locales() or [_FALLBACK_NO_NON_BASE],
)
def test_paridad_claves_parametros(lang: str) -> None:
    """Un local alterno no añade ni elimina llaves ni parámetros respecto al base."""
    if lang == _FALLBACK_NO_NON_BASE:
        pytest.skip("No hay locales alternos definidos")

    base = _load_locale(BASE_LOCALE)
    other = _load_locale(lang)
    errores = []

    for category in CATEGORIES:
        base_category = getattr(base, category)
        other_category = getattr(other, category)
        base_keys = set(base_category)
        other_keys = set(other_category)

        for llave in sorted(base_keys - other_keys):
            errores.append(f"{lang}.{category} pierde la llave {llave!r} del base")
        for llave in sorted(other_keys - base_keys):
            errores.append(
                f"{lang}.{category} añade la llave extra {llave!r} "
                f"no presente en el base"
            )

        for llave in sorted(base_keys & other_keys):
            base_params = _parameters(base_category[llave])
            other_params = _parameters(other_category[llave])
            for param in sorted(base_params - other_params):
                errores.append(
                    f"{lang}.{category}[{llave!r}] pierde el parámetro {{{param}}}"
                )
            for param in sorted(other_params - base_params):
                errores.append(
                    f"{lang}.{category}[{llave!r}] añade el parámetro extra {{{param}}}"
                )

    assert not errores, "\n".join(errores)


# ─── 5) Uso de cada llave en el proyecto ─────────────────────────────────


def _source_text() -> str:
    """Concatena el contenido de los .py de `src/` (excluyendo el paquete locales)."""
    bloques = []
    for path in _SRC_DIR.rglob("*.py"):
        if _PACKAGE_DIR in path.parents:
            continue
        bloques.append(path.read_text(encoding="utf-8"))
    return "\n".join(bloques)


def _referenced_loci(category: str, key: str, source: str) -> bool:
    """Indica si la llave `key` de `category` se referencia en `source`.

    La llave puede aparecer literalmente (con comillas, en cualquier acceso
    `locales.*["..."]`, `logger.*(key="...")` o `message_key = "..."`) o ser
    referenciada de forma dinámica, caso de los comandos:
    - `Cli["{comando}_help"]` se construye con un f-string.
    - `Progress[self.name]` usa el nombre del comando en tiempo de ejecución.
    """
    if re.search(r'["\']' + re.escape(key) + r'["\']', source):
        return True
    if (
        category == "Cli"
        and key.endswith("_help")
        and re.search(r'f"\{[^}]*}_help"', source)
    ):
        return True
    if category == "Progress" and re.search(r"Progress\[\s*\w+\s*\]", source):
        return True
    return False


def test_cada_llave_se_usa_en_el_proyecto() -> None:
    """Cada llave del local base se referencia en el código de `src/`."""
    if not list(_SRC_DIR.rglob("*.py")):
        pytest.skip("No hay código en src/ que consultar")

    base = _load_locale(BASE_LOCALE)
    source = _source_text()
    errores = []
    for category in CATEGORIES:
        for key in getattr(base, category):
            if not _referenced_loci(category, key, source):
                errores.append(f"{category}[{key}]: no parece usarse en src/")
    assert not errores, "\n".join(errores)
