"""Build a single-file pymedia.exe with PyInstaller.

Uso:
    uv run python scripts/build_windows.py

Genera `build/pymedia.exe` (onefile) incluyendo icono y los datos
de `pymedia.locales`/`pymedia.resources`.
"""

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "build" / "pyinstaller"
FINAL_PATH = ROOT / "build" / "pymedia.exe"
ENTRY = ROOT / "src" / "pymedia" / "main.py"
SRC = ROOT / "src"
ICON = ROOT / "src" / "pymedia" / "resources" / "icon.ico"


def main() -> None:
    """Compila pyMedia con PyInstaller en un único ejecutable `.exe`."""
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--noconfirm",
        "--clean",
        "--name",
        "pymedia",
        "--console",
        f"--icon={ICON}",
        "--collect-all=pymedia",
        "--collect-all=shellingham",
        "--collect-all=typer",
        f"--paths={SRC}",
        f"--distpath={OUTPUT_DIR / 'dist'}",
        f"--workpath={OUTPUT_DIR / 'work'}",
        f"--specpath={OUTPUT_DIR / 'spec'}",
        str(ENTRY),
    ]
    print("Compilando con PyInstaller... (esto puede tardar algunos minutos)")
    subprocess.run(cmd, check=True)

    produced = OUTPUT_DIR / "dist" / "pymedia.exe"
    if produced.exists():
        shutil.move(str(produced), str(FINAL_PATH))
        print(f"Listo: {FINAL_PATH}")
    else:
        raise SystemExit(f"No se encontró {produced}. Revisa la salida de PyInstaller.")


if __name__ == "__main__":
    main()
