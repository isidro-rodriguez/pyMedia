# Conceptos básicos

Este documento explica las reglas comunes a todos los comandos. Conocerlas evita la
mayoría de errores de uso.

## Anatomía de un comando

```bash
pymedia <comando> <entrada> [entrada ...] [opciones]
```

- Los comandos se agrupan en análisis, vídeo, audio, subtítulos e imagen.
- `pymedia` sin argumentos, o `pymedia <comando>` sin argumentos, muestra la ayuda.
- La ayuda de cada comando está traducida e incluye ejemplos: `pymedia cut --help`.

## Pistas e índices

Un contenedor (`.mkv`, `.mp4`…) agrupa pistas de vídeo, audio y subtítulos. pyMedia
numera las pistas **por tipo y empezando en 0**: la primera pista de audio es la `0`,
la segunda la `1`, y lo mismo con los subtítulos, con independencia de su posición
global en el fichero.

Consulta siempre los índices con `info` antes de usar `--track` o `--tracks`:

```bash
pymedia info pelicula.mkv
pymedia delete-audio pelicula.mkv --tracks 1,2
pymedia edit-subs pelicula.mkv --track 0 --default
```

- `--track N` (edición) acepta un único índice.
- `--tracks N,M,...` (borrado, extracción, transcodificación de audio) acepta una
  lista separada por comas, sin espacios.
- Un índice inexistente o negativo se rechaza antes de ejecutar ffmpeg.

## Marcas de tiempo

Las opciones `--at`, `--start` y `--end` aceptan tres formatos:

| Formato      | Ejemplo        | Equivale a                  |
|--------------|----------------|-----------------------------|
| `hh:mm:ss`   | `1:20:05`      | 1 h 20 min 5 s              |
| `mm:ss`      | `20:05`        | 20 min 5 s                  |
| `ss`         | `95`           | 1 min 35 s                  |

- Los segundos admiten decimales: `00:01:02.5`.
- Una marca igual o posterior a la duración del vídeo es un error.
- En listas (`--at`), las marcas deben ir en orden ascendente y sin duplicados.
- `--at` no se puede combinar con `--start` ni `--end`.

## Ficheros de salida

### Nombre por defecto

Si no indicas `-o`, la salida se crea **en el directorio actual** con el nombre de la
entrada, un sufijo que identifica la operación y la extensión que corresponda:

| Comando         | Sufijo               | Extensión                                       |
|-----------------|----------------------|-------------------------------------------------|
| `sheet`         | `_sheet`             | `default_containers.image`                      |
| `transcode`     | `_transcoded`        | `default_containers.media`                      |
| `cut`           | `_split`             | La de la entrada                                |
| `add-audio`     | `_added_audio`       | La de la entrada                                |
| `delete-audio`  | `_deleted_audio`     | La de la entrada                                |
| `edit-audio`    | `_edited_audio`      | La de la entrada                                |
| `extract-audio` | `_extracted_audio`   | `default_containers.audio_track`                |
| `add-subs`      | `_added_subs`        | La de la entrada                                |
| `delete-subs`   | `_deleted_subs`      | La de la entrada                                |
| `edit-subs`     | `_edited_subs`       | La de la entrada                                |
| `extract-subs`  | `_extracted_subs`    | `default_containers.subtitles`                  |
| `animated`      | (ninguno)            | `default_containers.animated_image`             |
| `frames`, `interval`, `scene` | `_thumbnail` | `default_containers.image`               |

Las extensiones `default_containers.*` se configuran en
[`config.toml`](configuracion.md#default_containers). `remux` y `join` exigen `-o`.

### Salidas múltiples

Algunos comandos generan varios ficheros a partir del nombre de salida:

| Comando                     | Patrón                                   | Ejemplo                          |
|-----------------------------|------------------------------------------|----------------------------------|
| `cut --at`                  | `<nombre>_NNN`                           | `video_split_000.mp4`            |
| `interval`, `scene`         | `<nombre>_NNN`                           | `video_thumbnail_004.jpg`        |
| `frames`                    | `<nombre>_<marca>` (`:` pasa a `-`)      | `video_thumbnail_0-01-30.jpg`    |
| `extract-audio`             | `<nombre>_audio_track_<N>`               | `video_extracted_audio_audio_track_1.m4a` |
| `extract-subs`              | `<nombre>_subtitles_track_<N>`           | `video_extracted_subs_subtitles_track_0.srt` |

### Reglas de validación

- La salida nunca puede ser el propio fichero de entrada.
- El nombre no puede contener `< > : " / \ | ? *`, terminar en espacio o punto, ni
  ser un nombre reservado de Windows (`CON`, `NUL`, `COM1`…).
- El directorio de destino se crea si no existe.
- La extensión debe ser compatible con los códecs de las pistas que se copian. Si no
  lo es, el error indica qué contenedores son válidos.

## Sobrescritura

`-ov` / `--overwrite` define qué hacer si una salida ya existe:

| Valor           | Comportamiento                                                              |
|-----------------|-----------------------------------------------------------------------------|
| `ask` (defecto) | Pregunta. Si respondes que sí, se aplica `yes` al resto del lote.          |
| `yes`           | Sobrescribe sin preguntar.                                                  |
| `no`            | Omite la operación con un aviso y continúa.                                 |

## Escritura segura

ffmpeg nunca escribe directamente en el destino. pyMedia crea un directorio temporal
oculto `.pymedia-*` junto a la salida, ejecuta ffmpeg sobre él y solo mueve los
ficheros al destino cuando el proceso termina con éxito. Por tanto:

- Un fallo, un bloqueo o `Ctrl+C` no dejan ficheros a medias.
- Un fichero existente no se toca hasta que la nueva versión está completa.
- El temporal se elimina siempre al terminar.

## Progreso y bloqueos

Cada ejecución muestra una barra de progreso de Rich. Si ffmpeg no produce actividad
durante `app.stall_timeout` segundos (60 por defecto), pyMedia lo da por bloqueado,
lo detiene y muestra el error. Ajusta el valor en [Configuración](configuracion.md#app).

## Lotes

`sheet` y `transcode` aceptan varios ficheros de entrada. En ese caso:

- `-o` no está permitido; usa `-d` / `--directory` para elegir el directorio de salida.
- `-o` y `-d` son excluyentes.
- Cada fichero se procesa por separado con su nombre por defecto.

```bash
pymedia transcode *.mkv --preset fast --video -d convertidos/
```

## Opciones comunes

| Opción                | Disponible en                                   | Efecto                                                           |
|-----------------------|-------------------------------------------------|------------------------------------------------------------------|
| `-o`, `--output`      | Todos salvo `info` y `play`                     | Ruta del fichero de salida.                                      |
| `-d`, `--directory`   | `sheet`, `transcode`                            | Directorio de salida para lotes.                                 |
| `-ov`, `--overwrite`  | Todos salvo `info` y `play`                     | `yes`, `no` o `ask`.                                             |
| `--strip-metadata`    | `add-audio`, `add-subs`, `cut`, `extract-audio`, `extract-subs`, `join`, `remux`, `transcode` | No copia los metadatos del origen (`-map_metadata -1`): título, etiquetas e idioma y título de cada pista. Las disposiciones (`default`, `forced`…) se conservan. |
| `--show-cmd`          | Todos salvo `info`                              | Muestra el comando ffmpeg (o ffplay) y sale sin ejecutarlo.      |
| `--debug`             | Todos                                           | Log detallado y confirmación antes de ejecutar ffmpeg.           |
| `--help`              | Todos                                           | Ayuda del comando.                                               |

### `--show-cmd`

Imprime el comando listo para copiar en la shell, con las rutas entrecomilladas según
el sistema operativo. Útil para aprender ffmpeg o para ajustar un comando a mano.

```bash
pymedia remux input.mkv -o output.mp4 --show-cmd
```

### `--debug`

Activa el nivel de log `DEBUG`: muestra los datos de `ffprobe`, el comando completo y
pide confirmación antes de lanzarlo. El log también se escribe en el fichero
[`logging.log`](configuracion.md#registro).
