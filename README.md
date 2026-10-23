# pyMedia

[![CI](https://github.com/isidro-rodriguez/pyMedia/actions/workflows/ci.yml/badge.svg)](https://github.com/isidro-rodriguez/pyMedia/actions/workflows/ci.yml)

CLI sencilla para `ffmpeg`, pensada para el usuario medio. Analiza, corta, une,
convierte y edita vídeos, pistas de audio y subtítulos con comandos cortos y
legibles, sin tener que recordar la sintaxis de ffmpeg.

- **Seguro:** valida las entradas antes de ejecutar y nunca deja ficheros a medias.
- **Rápido:** las operaciones sin pérdida (`remux`, `cut`, `join`) copian sin recodificar.
- **Configurable:** perfiles de transcodificación editables en `config.toml`.
- **En tu idioma:** interfaz en español e inglés.

## Instalación

Requisitos: Python 3.12+, [uv](https://docs.astral.sh/uv/) y
[ffmpeg](https://ffmpeg.org/download.html) (con ffprobe) en el `PATH`.

```bash
git clone https://github.com/isidro-rodriguez/pyMedia.git
cd pyMedia
uv tool install .
pymedia --version
```

También puedes compilar un ejecutable único con `uv run python scripts/build.py`.
Más opciones en [Instalación](docs/usuario/instalacion.md).

## Uso

```bash
pymedia --help               # lista de comandos
pymedia <comando> --help     # ayuda y ejemplos de un comando
```

| Comando         | Ejemplo                                                      |
|-----------------|--------------------------------------------------------------|
| `info`          | `pymedia info video.mp4`                                     |
| `sheet`         | `pymedia sheet video.mp4 --preset fhd -o hoja.webp`          |
| `transcode`     | `pymedia transcode video.mkv --preset slow --video --audio 0` |
| `remux`         | `pymedia remux video.mp4 -o video.mkv`                       |
| `cut`           | `pymedia cut video.mp4 --at 10:05,40:30`                     |
| `join`          | `pymedia join parte1.mp4 parte2.mp4 -o completo.mp4`         |
| `add-audio`     | `pymedia add-audio video.mp4 doblaje.m4a`                    |
| `delete-audio`  | `pymedia delete-audio video.mp4 --tracks 1,2`                |
| `edit-audio`    | `pymedia edit-audio video.mp4 --track 0 --language spa --default` |
| `extract-audio` | `pymedia extract-audio video.mp4 --tracks 1`                 |
| `add-subs`      | `pymedia add-subs video.mp4 subs.srt --language spa`         |
| `delete-subs`   | `pymedia delete-subs video.mp4 --tracks 0`                   |
| `edit-subs`     | `pymedia edit-subs video.mp4 --track 0 --forced`             |
| `extract-subs`  | `pymedia extract-subs video.mkv --tracks 0`                  |
| `animated`      | `pymedia animated video.mp4 --start 0:05 --end 0:12`         |
| `frames`        | `pymedia frames video.mp4 --at 1:30,5:15`                    |
| `interval`      | `pymedia interval video.mp4 --every 60`                      |
| `scene`         | `pymedia scene video.mp4 --scene 0.3`                        |

Consulta los índices de pista con `info` (empiezan en 0 por tipo) y añade
`--show-cmd` a cualquier comando para ver el comando ffmpeg sin ejecutarlo.
Referencia completa en [Comandos](docs/index.md#guía-de-usuario).

## Configuración

En el primer arranque se crea `config.toml` en el directorio de configuración del
usuario (`%APPDATA%\pymedia` en Windows, `~/.config/pymedia` en Linux,
`~/Library/Application Support/pymedia` en macOS). Permite ajustar:

- Los perfiles `fast`, `even` y `slow` de `transcode` (códec, calidad y audio).
- Los contenedores por defecto de cada tipo de salida.
- El idioma y el tiempo máximo de espera ante bloqueos de ffmpeg.

Detalles en [Configuración](docs/usuario/configuracion.md).

## Desarrollo

```bash
uv sync
uv run ruff format . && uv run ruff check . && uv run ty check && uv run pytest
```

Arquitectura, tests, traducciones y flujo de versiones en la
[guía de desarrollo](docs/index.md#guía-de-desarrollo).

## Documentación

- [Índice de la documentación](docs/index.md)
- [Conceptos básicos](docs/usuario/conceptos.md): pistas, marcas de tiempo, salidas y sobrescritura.
- [Formatos y compatibilidad](docs/usuario/formatos.md)
- [Solución de problemas](docs/usuario/problemas.md)
- [Arquitectura](docs/desarrollo/arquitectura.md)
- [CHANGELOG](CHANGELOG.md)

## Licencia

[MIT](LICENSE).
