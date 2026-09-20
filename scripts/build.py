"""Build a single-file pyMedia executable with PyInstaller.

Uso:
    uv run python scripts/build.py

Genera:
    Windows: build/pymedia.exe
    Linux/macOS: build/pymedia

Incluye el icono y los datos de `pymedia.locales`/`pymedia.resources`.
"""

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "build" / "pyinstaller"
ENTRY = ROOT / "src" / "pymedia" / "main.py"
SRC = ROOT / "src"

RESOURCES = ROOT / "src" / "pymedia" / "resources"
ICON_ICO = RESOURCES / "icon.ico"
ICON_PNG = RESOURCES / "icon.png"


def get_icon() -> Path | None:
    """Devuelve el icono apropiado para la plataforma actual."""
    if sys.platform == "win32":
        return ICON_ICO

    return ICON_PNG


def get_executable_name() -> str:
    """Devuelve el nombre del ejecutable para la plataforma actual."""
    if sys.platform == "win32":
        return "pymedia.exe"

    return "pymedia"


def main() -> None:
    """Compila pyMedia como ejecutable standalone con PyInstaller."""
    icon = get_icon()
    executable_name = get_executable_name()
    final_path = ROOT / "build" / executable_name

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
        "--collect-all=pymedia",
        "--collect-all=shellingham",
        "--collect-all=typer",
        f"--paths={SRC}",
        f"--distpath={OUTPUT_DIR / 'dist'}",
        f"--workpath={OUTPUT_DIR / 'work'}",
        f"--specpath={OUTPUT_DIR / 'spec'}",
        str(ENTRY),
    ]

    if icon is not None:
        if not icon.exists():
            raise SystemExit(f"No se encontró el icono: {icon}")

        cmd.insert(-1, f"--icon={icon}")

    print(f"Plataforma: {sys.platform}")
    print(f"Icono: {icon}")
    print("Compilando con PyInstaller... (esto puede tardar algunos minutos)")

    subprocess.run(cmd, check=True)

    produced = OUTPUT_DIR / "dist" / executable_name

    if produced.exists():
        final_path.parent.mkdir(parents=True, exist_ok=True)

        if final_path.exists():
            final_path.unlink()

        shutil.move(str(produced), str(final_path))
        print(f"Listo: {final_path}")
    else:
        raise SystemExit(f"No se encontró {produced}. Revisa la salida de PyInstaller.")


if __name__ == "__main__":
    main()
