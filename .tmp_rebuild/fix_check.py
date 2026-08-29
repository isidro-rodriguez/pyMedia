import pathlib

p = pathlib.Path("scripts/locale_manager.py")
s = p.read_text(encoding="utf-8")

old = "        for msgid, message in catalog.items():"
new = "        for message in catalog:\n            msgid = message.id"

s = s.replace(old, new)
assert new in s, "no se pudo aplicar el fix"

p.write_text(s, encoding="utf-8")
print("OK: cmd_check iteración corregida")
