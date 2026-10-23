# pyMedia

[![CI](https://github.com/isidro-rodriguez/pyMedia/actions/workflows/ci.yaml/badge.svg)](https://github.com/isidro-rodriguez/pyMedia/actions/workflows/ci.yaml)
[![Docs](https://github.com/isidro-rodriguez/pyMedia/actions/workflows/docs.yml/badge.svg)](https://isidro-rodriguez.github.io/pyMedia/)

CLI sencilla para `ffmpeg`, pensada para el usuario medio. Analiza, corta, une,
convierte y edita vídeos, pistas de audio y subtítulos con comandos cortos y
legibles, sin tener que recordar la sintaxis de ffmpeg.

📖 **Documentación:** <https://isidro-rodriguez.github.io/pyMedia/>

- **Seguro:** valida las entradas antes de ejecutar y nunca deja ficheros a medias.
- **Rápido:** las operaciones sin pérdida (`remux`, `cut`, `join`) copian sin recodificar.
- **Configurable:** perfiles de transcodificación editables en `config.toml`.
- **En tu idioma:** interfaz en español e inglés.

## Instalación

Descarga el paquete de tu sistema desde [Releases](https://github.com/isidro-rodriguez/pyMedia/releases/latest):

```bash
sudo apt install ./pymedia_1.0.0_amd64.deb      # Linux (instala ffmpeg como dependencia)
```

En Windows, descomprime `pymedia-1.0.0-windows-x64.zip`, añade la carpeta al `PATH` e
instala [ffmpeg](https://ffmpeg.org/download.html) (`winget install ffmpeg`).

Desde el código fuente (Python 3.12+, [uv](https://docs.astral.sh/uv/) y ffmpeg en el `PATH`):

```bash
git clone https://github.com/isidro-rodriguez/pyMedia.git
cd pyMedia
uv tool install .
pymedia --version
```

Más opciones en [Instalación](https://isidro-rodriguez.github.io/pyMedia/usuario/instalacion/).

## Uso

```bash
pymedia --help               # lista de comandos
pymedia <comando> --help     # ayuda y ejemplos de un comando
```

| Comando         | Ejemplo                                                           |
| --------------- | ----------------------------------------------------------------- |
| `info`          | `pymedia info video.mp4`                                          |
| `sheet`         | `pymedia sheet video.mp4 --preset fhd -o hoja.webp`               |
| `play`          | `pymedia play video.mkv --start 10:00 --audio 1`                  |
| `transcode`     | `pymedia transcode video.mkv --preset slow --video --audio 0`     |
| `remux`         | `pymedia remux video.mp4 -o video.mkv`                            |
| `cut`           | `pymedia cut video.mp4 --at 10:05,40:30`                          |
| `join`          | `pymedia join parte1.mp4 parte2.mp4 -o completo.mp4`              |
| `add-audio`     | `pymedia add-audio video.mp4 doblaje.m4a`                         |
| `delete-audio`  | `pymedia delete-audio video.mp4 --tracks 1,2`                     |
| `edit-audio`    | `pymedia edit-audio video.mp4 --track 0 --language spa --default` |
| `extract-audio` | `pymedia extract-audio video.mp4 --tracks 1`                      |
| `add-subs`      | `pymedia add-subs video.mp4 subs.srt --language spa`              |
| `delete-subs`   | `pymedia delete-subs video.mp4 --tracks 0`                        |
| `edit-subs`     | `pymedia edit-subs video.mp4 --track 0 --forced`                  |
| `extract-subs`  | `pymedia extract-subs video.mkv --tracks 0`                       |
| `animated`      | `pymedia animated video.mp4 --start 0:05 --end 0:12`              |
| `frames`        | `pymedia frames video.mp4 --at 1:30,5:15`                         |
| `interval`      | `pymedia interval video.mp4 --every 60`                           |
| `scene`         | `pymedia scene video.mp4 --scene 0.3`                             |

Consulta los índices de pista con `info` (empiezan en 0 por tipo) y añade
`--show-cmd` a cualquier comando para ver el comando ffmpeg sin ejecutarlo.
Referencia completa en [Comandos](https://isidro-rodriguez.github.io/pyMedia/usuario/comandos/analisis/).

## Configuración

En el primer arranque se crea `config.toml` en el directorio de configuración del
usuario (`%APPDATA%\pymedia` en Windows, `~/.config/pymedia` en Linux,
`~/Library/Application Support/pymedia` en macOS). Permite ajustar:

- Los perfiles `fast`, `even` y `slow` de `transcode` (códec, calidad y audio).
- Los contenedores por defecto de cada tipo de salida.
- El idioma y el tiempo máximo de espera ante bloqueos de ffmpeg.

Detalles en [Configuración](https://isidro-rodriguez.github.io/pyMedia/usuario/configuracion/).

## Desarrollo

```bash
uv sync
uv run ruff format . && uv run ruff check . && uv run ty check && uv run pytest
```

Arquitectura, tests, traducciones y flujo de versiones en la
[guía de desarrollo](https://isidro-rodriguez.github.io/pyMedia/desarrollo/arquitectura/).

## Documentación

La documentación completa se publica en <https://isidro-rodriguez.github.io/pyMedia/>:

- [Conceptos básicos](https://isidro-rodriguez.github.io/pyMedia/usuario/conceptos/): pistas, marcas de tiempo, salidas y sobrescritura.
- [Formatos y compatibilidad](https://isidro-rodriguez.github.io/pyMedia/usuario/formatos/)
- [Solución de problemas](https://isidro-rodriguez.github.io/pyMedia/usuario/problemas/)
- [Arquitectura](https://isidro-rodriguez.github.io/pyMedia/desarrollo/arquitectura/)
- [CHANGELOG](CHANGELOG.md)

Las fuentes están en `docs/` y se generan con [Zensical](https://zensical.org/):

```bash
uv run zensical serve        # vista previa en http://localhost:8000
uv run zensical build        # sitio estático en site/
```

## Licencia

[MIT](LICENSE).
