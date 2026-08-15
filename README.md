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
uv run pymedia
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

## Ejemplos de comandos

```bash
pymedia                                           # Muestra la ayuda
pymedia concat video1.mp4 video2.mp4 video3.mp4   # Une los vídeos en el orden aportado
pymedia encode video.mp4 -r                       # Recodifica el vídeo
pymedia encode video.mp4 -s 720                   # Reescala el vídeo a 720p                 
pymedia encode video.mp4 -c 200,200,0,0           # Corta la imagen 200 px por la izquiera y derecha
pymedia split video.mp4 -t 10,20,1:30             # Divide el vídeo a los puntos 0:10, 0:20 y 1:30
pymedia gif video.mp4                             # Genera un gif animado
```

## Opciones

| Opción          | Flag  | Descripción                                     | Ejemplo          |
|-----------------|-------| ----------------------------------------------- | ---------------- |
| `--crop`        | `-c`  | Recorta píxeles (`IZQ,DER,ARRIBA,ABAJO`)        | `-c 200,200,0,0` |
| `--scale`       | `-s`  | Redimensiona a la altura indicada               | `-s 720`         |
| `--gyrate`      | `-g`  | Gira el ángulo indicado (`90`, `180`, `270`)    | `-g 90`          |
| `--remux`       | `-r`  | Recodifica con el perfil de la configuración    | `-r`             |
| `--output`      | `-o`  | Nombre del archivo de salida                    | `-o corte.mp4`   |
| `--fps`         | `-f`  | Imágenes por segundo del gif (por defecto `15`) | `-f 12`          |
| `--start-point` | `-sp` | Inicio temporal del gif (`hh:mm:ss`)            | `-sp 1:20`       |
| `--end-point`   | `-ep` | Fin temporal del gif (`hh:mm:ss`)               | `-ep 1:40`       |
| `--trim-points` | `-t`  | Puntos de corte para `split`                    | `-t 00:20,00:30` |

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
video_codec = "h264"                # h264 | h265 | av1
video_preset = "fast"
video_crf = 22
audio_codec = "aac"                 # aac | opus | eac3
audio_bit_rate = "160k"
default_container = ".mp4"

[conflictive_join]
resize_to = "min_height"            # min_height | max_height
fps = "min_fps"                     # min_fps | max_fps
channels = "stereo"                 # stereo | mono | 5.1
confirm_encode = true

[app]
language = "system"                 # system | english | spanish | italian | french | german
disable_resolution_increase = true
```

Los logs se escriben en `pymedia/logging.log` dentro del mismo directorio de configuración.
