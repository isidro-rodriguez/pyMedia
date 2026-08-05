# pyMedia

Aplicación de consola (CLI) que actúa como handler de comandos `ffmpeg` para tareas habituales de procesamiento de vídeo: unir, transcodificar, dividir y generar gifs animados.

> Estado: **Alpha** (en pruebas locales).

---

## Requisitos

- **ffmpeg** y **ffprobe** instalados y disponibles en el `PATH`.
  - Windows: `winget install ffmpeg` o <https://ffmpeg.org/download.html>
  - Debian/Ubuntu: `sudo apt install ffmpeg`

---

## Instalación

### Desde fuente (desarrollo)

```bash
# Crear entorno e instalar dependencias
uv sync

# Ejecutar la CLI
uv run main --help
```

### Compilar a exe (Windows)

```bash
# Genera build/pymedia.exe (tarda varios minutos la primera vez)
uv run python build.py
```

Colocar el exe en el `PATH`:

```powershell
copy build\pymedia.exe "$env:LOCALAPPDATA\Microsoft\WindowsApps\pymedia.exe"
```

Ahora `pymedia` se puede invocar desde cualquier terminal.

---

## Comandos

### `tui` (por defecto)

Lanza la interfaz de usuario en terminal.

```bash
pymedia            # equivale a: pymedia tui
```

### `concat`

Une los vídeos en el orden aportado.

```bash
pymedia concat video1.mp4 video2.mp4 video3.mp4
pymedia concat *.mp4 -o unido.mp4
```

### `encode`

Transcodifica con las opciones elegidas (requiere al menos una).

```bash
pymedia encode video.mp4 -s 720 -g 90 -o redimensionado.mp4
pymedia encode video.mp4 -c 200,200,0,0 -o recortado.mp4
pymedia encode video.mp4 -r -o remuxed.mp4
```

### `split`

Separa un vídeo en los puntos de corte indicados.

```bash
pymedia split video.mp4 -t 00:10,00:20,00:30
```

### `gif`

Genera un gif animado del vídeo aportado.

```bash
pymedia gif video.mp4 -o clip.gif
pymedia gif video.mp4 -f 12 -s 480 -sp 1:20 -ep 1:40 -o fragmento.gif
```

---

## Opciones

| Opción              | Flag            | Descripción                                              | Ejemplo              |
| ------------------- | --------------- | -------------------------------------------------------- | -------------------- |
| `--crop`            | `-c`            | Recorta píxeles (`IZQ,DER,ARRIBA,ABAJO`)                 | `-c 200,200,0,0`     |
| `--scale`           | `-s`            | Redimensiona a la altura indicada                        | `-s 720`             |
| `--gyrate`          | `-g`            | Gira el ángulo indicado (`90`, `180`, `270`)             | `-g 90`              |
| `--remux`           | `-r`            | Recodifica con el perfil de la configuración             | `-r`                 |
| `--output`          | `-o`            | Nombre del archivo de salida                             | `-o corte.mp4`       |
| `--fps`             | `-f`            | Imágenes por segundo del gif (por defecto `15`)          | `-f 12`              |
| `--start-point`     | `-sp`           | Inicio temporal del gif (`hh:mm:ss`)                    | `-sp 1:20`           |
| `--end-point`       | `-ep`           | Fin temporal del gif (`hh:mm:ss`)                        | `-ep 1:40`           |
| `--trim-points`     | `-t`            | Puntos de corte para `split`                             | `-t 00:10,00:20,00:30` |

**Alturas disponibles para `--scale`:**

- Vídeo: `480`, `720`, `1080`, `1440`, `2160`
- Gif: `240`, `480`, `720`

---

## Configuración

En el primer arranque se copia un `config.toml` por defecto a:

- **Windows**: `%APPDATA%\pymedia\config.toml`
- **Linux**: `~/.config/pymedia/config.toml`

```toml
[encode]
video_codec = "libx264"     # libx264 | libx265 | libsvtav1
video_preset = "fast"
video_crf = "22"
video_pix_fmt = "yuv420p"
audio_codec = "aac"
audio_bit_rate = "160k"

[conflictive_join]
resize_to = "min_height"    # min_height | max_height
fps = "min"                 # min | max
channels = "stereo"         # stereo | mono
pix_fmt = "yuv420p"         # yuv420p | yuv420p10le
confirm_encode = true

[app]
logger_level = "INFO"       # DEBUG | INFO | WARNING | ERROR
```

Los logs se escriben en `pymedia/logging.log` dentro del mismo directorio de configuración.

---

## Desarrollo

```bash
uv sync                 # instalar dependencias
uv run pytest           # ejecutar tests
uv run ruff check       # lint
uv run ruff format      # formatear
```
