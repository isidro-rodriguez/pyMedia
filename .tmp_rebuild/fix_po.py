import pathlib
from babel.messages.pofile import read_po, write_po

po_path = pathlib.Path("src/pymedia/locales/es/LC_MESSAGES/pymedia.po")

with po_path.open("rb") as f:
    catalog = read_po(f)

# Traducciones faltantes (cadenas nuevas no presentes en el viejo es.py)
faltantes = {
    "Command options": "Opciones de comando",
    "Output options": "Opciones de salida",
    "Invalid configuration setting: conflictive_concat.height is expected one "
    "of: %(expected)s.": "Ajuste de configuración no válido: se espera que "
    "conflictive_concat.height sea uno de: %(expected)s.",
}

for msgid, msgstr in faltantes.items():
    msg = catalog.get(msgid)
    if msg is not None:
        msg.string = msgstr
        print(f"  traducido: {msgid!r}")
    else:
        print(f"  NO ENCONTRADO: {msgid!r}")

with po_path.open("wb") as f:
    write_po(f, catalog)

print("OK: es.po actualizado")
