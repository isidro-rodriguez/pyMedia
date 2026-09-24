"""Gestión de los catálogos gettext de pyMedia.

Comandos:
    extract             Genera `pymedia.pot` a partir de los msgid de `src/`.
    update -l <lang>    Sincroniza `<lang>.po` con el POT actual.
    compile -l <lang>   Compila `pymedia.po` a `pymedia.mo`.
    check               Valida los catálogos y el POT.

Uso, ejemplo en español:
    1. Regenera pymedia.pot escaneando `_()` y `ngettext()` de src/
    uv run python scripts/i18n.py extract

    2. Rehace spanish/LC_MESSAGES/pymedia.po a partir del POT
    uv run python scripts/i18n.py update -l spanish

    3. Manual: abrir src/pymedia/locales/spanish/LC_MESSAGES/pymedia.po y
       rellenar las msgstr vacía

    4. Compila pymedia.po -> pymedia.mo
    uv run python scripts/i18n.py compile -l spanish

    5. Validación
    uv run python scripts/i18n.py check
    uv run pytest tests/test_locales.py tests/test_locale_manager.py
"""

import argparse
import io
import re
import sys
from pathlib import Path

from babel.messages.catalog import Catalog
from babel.messages.extract import extract_from_dir
from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po, write_po

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
LOCALEDIR = SRC_DIR / "pymedia" / "locales"
DOMAIN = "pymedia"
LANGUAGES = ["spanish"]


def _po_path(lang: str) -> Path:
    """Devuelve la ruta al archivo `.po` del idioma indicado."""
    return LOCALEDIR / lang / "LC_MESSAGES" / f"{DOMAIN}.po"


def _extract_catalog() -> Catalog:
    """Extrae los msgid de los archivos Python de `src/`."""
    catalog = Catalog(domain=DOMAIN)
    for filename, lineno, message, _comments, context in extract_from_dir(
        str(SRC_DIR),
        keywords={"_": None, "ngettext": (1, 2)},
        directory_filter=lambda dirname: Path(dirname).name != "locales",
    ):
        if message is None or context is not None:
            continue
        catalog.add(message, locations=[(filename, lineno)])
    return catalog


def cmd_extract() -> None:
    """Regenera `pymedia.pot` desde el código fuente."""
    catalog = _extract_catalog()
    pot = LOCALEDIR / f"{DOMAIN}.pot"
    pot.parent.mkdir(parents=True, exist_ok=True)
    with pot.open("wb") as f:
        write_po(f, catalog)
    print(f"POT actualizado: {pot} ({len(catalog)} msgid)")


def cmd_update(lang: str) -> None:
    """Sincroniza `<lang>.po` con el POT.

    Args:
        lang: Nombre de idioma del catálogo (`spanish`, `english`...).
    """
    pot_path = LOCALEDIR / f"{DOMAIN}.pot"
    pot = read_po(pot_path.open("rb"))
    po_path = _po_path(lang)

    old = {}
    if po_path.exists():
        for msg in read_po(po_path.open("rb")):
            if msg.id:
                old[msg.id] = msg.string

    new_catalog = Catalog(domain=DOMAIN)
    for message in pot:
        if not message.id:
            continue
        msgstr = old.get(message.id, "")
        new_catalog.add(message.id, string=msgstr, locations=list(message.locations))

    write_catalog(new_catalog, po_path)
    print(f"Catálogo actualizado: {po_path} ({len(new_catalog)} entradas)")


def cmd_compile(lang: str) -> None:
    """Compila `<lang>.po` a `<lang>.mo`.

    Args:
        lang: Nombre de idioma del catálogo (`spanish`, `english`...).
    """
    po_path = _po_path(lang)
    if not po_path.exists():
        sys.exit(f"No existe {po_path}")
    catalog = read_po(po_path.open("rb"))
    mo_path = po_path.with_suffix(".mo")
    with mo_path.open("wb") as f:
        write_mo(f, catalog)
    print(f"Compilado: {mo_path}")


def write_catalog(catalog: Catalog, po_path: Path) -> None:
    """Escribe un catálogo en `po_path` creando el directorio padre.

    Args:
        catalog: Catálogo de mensajes a escribir.
        po_path: Ruta del fichero `.po` destino.
    """
    po_path.parent.mkdir(parents=True, exist_ok=True)
    with po_path.open("wb") as f:
        write_po(f, catalog)


def cmd_check() -> None:
    """Valida la sintaxis, unicidad, placeholders y compilación."""
    problems: list[str] = []

    pot_path = LOCALEDIR / f"{DOMAIN}.pot"
    if not pot_path.exists():
        problems.append(f"Falta el POT: {pot_path} (ejecuta `extract`)")

    for lang in LANGUAGES:
        po_path = _po_path(lang)
        if not po_path.exists():
            problems.append(f"Falta el catálogo: {po_path}")
            continue
        catalog = read_po(po_path.open("rb"))
        try:
            stream = io.BytesIO()
            write_mo(stream, catalog)
        except Exception as exc:
            problems.append(f"{lang}: no compila: {exc}")

        seen: set[str] = set()
        for message in catalog:
            msgid = message.id
            msgstr = message.string if isinstance(message.string, str) else ""
            if not isinstance(msgid, str) or not msgid:
                continue  # header o formas plurales del PO
            if not msgstr:
                problems.append(f"{lang}: msgstr vacío para {msgid!r}")
            if msgid in seen:
                problems.append(f"{lang}: msgid duplicado {msgid!r}")
            seen.add(msgid)
            if not _same_placeholders(msgid, msgstr):
                problems.append(
                    f"{lang}: placeholders distintos msgid/msgstr: {msgid!r}"
                )

    if problems:
        print("\n".join(sorted(set(problems))))
        sys.exit(1)
    print(f"Catálogos válidos: {', '.join(LANGUAGES)}")


def _same_placeholders(msgid: str, msgstr: str) -> bool:
    """Comprueba que msgid y msgstr tienen los mismos `%(name)s`."""
    pattern = re.compile(r"%\(\w+\)s")
    return set(pattern.findall(msgid)) == set(pattern.findall(msgstr))


def main() -> None:
    """Parsea los argumentos y ejecuta el subcomando i18n indicado."""
    parser = argparse.ArgumentParser(prog="locale_manager", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("extract", help="Genera pymedia.pot desde src/")
    for name in ("update", "compile"):
        p = sub.add_parser(name, help=f"{name.capitalize()} de catálogos")
        p.add_argument("-l", "--lang", default="spanish")
    sub.add_parser("check", help="Valida los catálogos")

    args = parser.parse_args()
    if args.command == "extract":
        cmd_extract()
    elif args.command == "check":
        cmd_check()
    elif args.command == "update":
        cmd_update(args.lang)
    elif args.command == "compile":
        cmd_compile(args.lang)


if __name__ == "__main__":
    main()
