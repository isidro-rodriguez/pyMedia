"""Build a single-file pymedia.exe with Nuitka.

Uso:
    uv run python build.py
"""

import shutil
import subprocess
import sys
from pathlib import Path

OUTPUT_DIR = Path("build")
ENTRY = "src/pymedia/main.py"
FINAL_NAME = "pymedia.exe"
RESOURCES = Path("src/pymedia/resources")
ICON = RESOURCES / "icon.ico"


def main() -> None:
    """Compila pyMedia con Nuitka en un único ejecutable `.exe`."""
    cmd = [
        sys.executable,
        "-m",
        "nuitka",
        "--onefile",
        "--standalone",
        f"--output-dir={OUTPUT_DIR}",
        "--include-package=pymedia",
        "--include-package-data=pymedia",
        f"--windows-icon-from-ico={ICON}",
        "--assume-yes-for-downloads",
        "--remove-output",
        ENTRY,
    ]
    print("Compilando con Nuitka... (esto puede tardar varios minutos)")
    subprocess.run(cmd, check=True)

    produced = OUTPUT_DIR / "main.exe"
    final = OUTPUT_DIR / FINAL_NAME
    if produced.exists():
        shutil.move(str(produced), str(final))
        print(f"Listo: {final}")
    else:
        print(f"No se encontró {produced}. Revisa la salida de Nuitka.")


if __name__ == "__main__":
    main()
