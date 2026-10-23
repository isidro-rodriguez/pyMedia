# Instalación

## Requisitos

| Requisito          | Versión          | Notas                                                          |
|--------------------|------------------|----------------------------------------------------------------|
| Python             | 3.12 o superior  | Solo para ejecutar desde el código fuente.                     |
| ffmpeg y ffprobe   | Reciente         | Deben estar en el `PATH`. pyMedia lo comprueba al arrancar.    |
| uv                 | Reciente         | Gestor de dependencias del proyecto.                           |

Instalación de ffmpeg según plataforma:

```bash
# Windows
winget install ffmpeg

# Debian / Ubuntu
sudo apt install ffmpeg

# macOS (Homebrew)
brew install ffmpeg
```

La transcodificación usa los codificadores `libx264`, `libx265`, `libsvtav1` y `libopus`
según el perfil elegido. Las compilaciones oficiales de ffmpeg los incluyen; si usas una
compilación mínima, comprueba que están disponibles con `ffmpeg -encoders`.

## Desde el código fuente

```bash
git clone https://github.com/isidro-rodriguez/pyMedia.git
cd pyMedia
uv sync
uv run pymedia --help
```

### Como herramienta global

`uv tool` instala el comando `pymedia` en el `PATH` del usuario, aislado en su propio
entorno:

```bash
uv tool install .            # instalar
uv tool install --force .    # actualizar tras un git pull
uv tool uninstall pymedia    # desinstalar
```

## Ejecutable único

`scripts/build.py` compila con PyInstaller un ejecutable autónomo con el icono, los
catálogos de traducción y los recursos incluidos. No requiere Python en la máquina
destino, pero sí ffmpeg.

```bash
uv run python scripts/build.py
```

| Plataforma   | Resultado               |
|--------------|-------------------------|
| Windows      | `build/pymedia.exe`     |
| Linux, macOS | `build/pymedia`         |

## Autocompletado de la shell

pyMedia usa Typer, que genera el autocompletado de bash, zsh, fish y PowerShell:

```bash
pymedia --install-completion   # instala el autocompletado de la shell actual
pymedia --show-completion      # muestra el script para personalizarlo
```

Reinicia la terminal tras instalarlo.

## Comprobación

```bash
pymedia --version
```

Muestra la versión de pyMedia, la de Python y la plataforma. Si ffmpeg o ffprobe no
están en el `PATH`, cualquier comando termina con un mensaje que lo indica.

## Primer arranque

En la primera ejecución pyMedia copia la configuración por defecto al directorio de
configuración del usuario. Consulta [Configuración](configuracion.md) para conocer la
ruta y las opciones.
