# Configuración

## Ubicación

En el primer arranque pyMedia copia `config.toml` al directorio de configuración del
usuario. Ese mismo directorio contiene el log y la tipografía de `sheet`.

| Plataforma | Directorio                                    |
|------------|-----------------------------------------------|
| Windows    | `%APPDATA%\pymedia\`                          |
| Linux      | `~/.config/pymedia/` (o `$XDG_CONFIG_HOME/pymedia/`) |
| macOS      | `~/Library/Application Support/pymedia/`      |

| Fichero                | Contenido                                     |
|------------------------|-----------------------------------------------|
| `config.toml`          | Configuración editable.                       |
| `logging.log`          | Log de ejecuciones (rotación diaria).         |
| `assets/`              | Tipografía usada por `sheet`.                 |

Para **restaurar los valores por defecto**, borra `config.toml`: se volverá a crear
en la siguiente ejecución.

## Fichero por defecto

```toml
[app]
language = "system"
stall_timeout = 60

[default_containers]
animated_image = ".gif"
audio_track = ".m4a"
image = ".jpg"
media = ".mp4"
subtitles = ".srt"

[transcode.fast]
video_codec = "h265"
video_preset = "veryfast"
video_crf = 25
audio_codec = "aac"
audio_bit_rate = "160k"

[transcode.even]
video_codec = "h265"
video_preset = "medium"
video_crf = 23
audio_codec = "aac"
audio_bit_rate = "192k"

[transcode.slow]
video_codec = "h265"
video_preset = "slower"
video_crf = 20
audio_codec = "aac"
audio_bit_rate = "256k"
```

## `[app]`

| Clave           | Valores                           | Descripción                                                    |
|-----------------|-----------------------------------|----------------------------------------------------------------|
| `language`      | `system`, `spanish`, `english` o alias | Idioma de la interfaz. Ver [Idioma](#idioma).             |
| `stall_timeout` | Entero de 30 a 600                | Segundos sin actividad de ffmpeg antes de darlo por bloqueado. |

Sube `stall_timeout` si trabajas con discos de red lentos o con codificadores muy
lentos (AV1 con preset bajo) y ves errores de bloqueo falsos.

## `[default_containers]`

Extensión usada cuando no indicas `-o` (ver [Nombre por defecto](conceptos.md#nombre-por-defecto)).

| Clave            | Valores admitidos                  | Usado por                          |
|------------------|------------------------------------|------------------------------------|
| `animated_image` | `.apng`, `.gif`, `.webp`           | `animated`                         |
| `image`          | `.jpeg`, `.jpg`, `.png`, `.webp`   | `sheet`, `frames`, `interval`, `scene` |
| `subtitles`      | `.ass`, `.srt`, `.ssa`             | `extract-subs`                     |
| `audio_track`    | Común a los códecs de audio de los tres perfiles | `extract-audio`      |
| `media`          | Común a los pares vídeo + audio de los tres perfiles | `transcode`                |

`audio_track` y `media` dependen de los perfiles: por ejemplo, con `opus` en algún
perfil, `.m4a` deja de ser válido y `.mkv`/`.webm` pasan a serlo. Si la combinación no
es válida, el error indica las extensiones posibles.

## `[transcode.<perfil>]`

Deben existir exactamente los perfiles `fast`, `even` y `slow`, y cada uno debe tener
las cinco claves.

| Clave            | Valores admitidos                                                         |
|------------------|---------------------------------------------------------------------------|
| `video_codec`    | `h264`, `h265`, `hevc` (alias de `h265`), `av1`                           |
| `video_preset`   | `h264`/`h265`: `ultrafast`, `superfast`, `veryfast`, `faster`, `fast`, `medium`, `slow`, `slower`, `veryslow`, `placebo`. `av1`: `0` a `14` (texto). |
| `video_crf`      | Entero. `h264`/`h265`: 0–51. `av1`: 0–63.                                 |
| `audio_codec`    | `aac`, `eac3`, `opus`                                                     |
| `audio_bit_rate` | `aac`: 96k–320k · `eac3`: 192k–640k · `opus`: 64k–256k (valores de [Formatos](formatos.md#códecs-de-transcodificación)). |

Ejemplo de perfil `slow` orientado a archivo en AV1 + Opus, guardado en MKV:

```toml
[default_containers]
media = ".mkv"
audio_track = ".mka"
# ...

[transcode.slow]
video_codec = "av1"
video_preset = "4"
video_crf = 30
audio_codec = "opus"
audio_bit_rate = "128k"
```

## Validación

pyMedia valida `config.toml` en cada ejecución y, si algo falla, muestra **todos** los
problemas a la vez sin ejecutar nada:

| Problema                              | Mensaje                                                           |
|---------------------------------------|-------------------------------------------------------------------|
| Sintaxis TOML incorrecta              | `El fichero de configuración no es un TOML válido: <ruta> (<motivo>)` |
| Falta una tabla (`[app]`…)            | `se espera que <tabla> sea una tabla`                             |
| Falta o sobra una clave               | `Falta el ajuste de configuración: <clave>` / `Ajuste de configuración desconocido: <clave>` |
| Perfiles distintos de fast/even/slow  | `se espera que los presets de transcode sean uno de: ...`         |
| Valor fuera de lista o rango          | `se espera que <clave> sea uno de: ...` / `... sea un entero entre X e Y` |

## Idioma

El idioma de la interfaz se decide con esta prioridad:

1. Variable de entorno `PYMEDIA_LANG`.
2. `app.language` de `config.toml` (si no es `system`).
3. Idioma del sistema (`LANGUAGE`, `LC_ALL`, `LC_MESSAGES`, `LANG` o el _locale_).
4. Inglés.

Tanto `PYMEDIA_LANG` como `app.language` aceptan el código ISO 639-1 (`es`), ISO 639-2
(`spa`), el nombre en inglés (`spanish`) o el nativo (`Español`). Un valor desconocido
se ignora y se pasa al siguiente nivel.

```bash
PYMEDIA_LANG=en pymedia --help         # Linux / macOS
$env:PYMEDIA_LANG="en"; pymedia --help # PowerShell
```

El idioma se fija antes de cargar los comandos, así que afecta también a la ayuda.

## Variables de entorno

| Variable            | Uso                                                                |
|---------------------|--------------------------------------------------------------------|
| `PYMEDIA_LANG`      | Fuerza el idioma de la interfaz.                                   |
| `PYMEDIA_LOCALEDIR` | Directorio alternativo de catálogos de traducción (builds empaquetados, pruebas). |

## Registro

| Destino  | Contenido                                                                           |
|----------|-------------------------------------------------------------------------------------|
| Consola  | Mensajes con formato y colores de Rich. Con `--debug`, también los de depuración.   |
| Fichero  | `logging.log`: fecha, nivel y mensaje de cada ejecución. Rota a medianoche y conserva 7 días. |

Ante un error, el log incluye el final de la salida de ffmpeg, útil para diagnosticar
(ver [Solución de problemas](problemas.md)).
