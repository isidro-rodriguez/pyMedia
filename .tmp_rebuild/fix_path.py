import pathlib

p = pathlib.Path("src/pymedia/locale_manager.py")
s = p.read_text(encoding="utf-8")

antes = "parents[1] / \"locales\""
despues = "parents[0] / \"locales\""

if antes in s:
    s = s.replace(antes, despues)
    p.write_text(s, encoding="utf-8")
    print("OK: parents[1] -> parents[0]")
else:
    print("NO ENCONTRADO:", antes)
    # Mostrar líneas relevante
    for i, line in enumerate(s.splitlines()):
        if "parents" in line and "locales" in line:
            print(f"  linea {i+1}: {line!r}")
