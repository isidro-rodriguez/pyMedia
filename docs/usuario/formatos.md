# Formatos y compatibilidad

pyMedia comprueba la compatibilidad entre códecs y contenedores **antes** de ejecutar
ffmpeg, a partir de los catálogos de `src/pymedia/data/`. Si una combinación no es
válida, el error indica las alternativas.

## Ficheros de entrada

| Tipo        | Extensiones aceptadas                                                                |
|-------------|--------------------------------------------------------------------------------------|
| Vídeo       | `.3g2` `.3gp` `.asf` `.avi` `.f4v` `.flv` `.m2ts` `.mkv` `.mov` `.mp4` `.mpeg` `.mpg` `.mts` `.mxf` `.ogg` `.ogv` `.rm` `.rmvb` `.ts` `.vob` `.webm` `.wmv` |
| Audio       | `.3gp` `.ac3` `.aiff` `.amr` `.au` `.avi` `.awb` `.flac` `.m2ts` `.m4a` `.mka` `.mkv` `.mlp` `.mov` `.mp1` `.mp2` `.mp3` `.mp4` `.mpeg` `.mpg` `.oga` `.ogg` `.opus` `.raw` `.rtp` `.thd` `.ts` `.vob` `.wav` `.webm` |
| Subtítulos  | `.srt` `.ass` `.ssa` para `add-subs` y `--burn-subtitles`                            |

La extensión es solo el primer filtro: ffprobe confirma después que el fichero tiene
el contenido esperado (por ejemplo, que un `.srt` es realmente SubRip).

## Ficheros de salida

| Operación                                    | Extensiones                         |
|----------------------------------------------|-------------------------------------|
| Vídeo (`transcode`, `remux`, `join`)         | `.mkv`, `.mp4`, `.webm`             |
| Vídeo editado (`cut`, `add-*`, `delete-*`, `edit-*`) | La de la entrada, o la indicada con `-o` si admite los códecs. |
| Pistas de audio (`extract-audio`)            | Según el códec (tabla de copia de audio). |
| Pistas de subtítulos (`extract-subs`)        | Según el códec (tabla de copia de subtítulos). |
| Imagen fija                                  | `.jpg`, `.jpeg`, `.png`, `.webp`    |
| Imagen animada                               | `.gif`, `.apng`, `.webp`            |

## Copia sin recodificar

Las operaciones con `-c copy` (`remux`, `cut`, `join`, comandos de audio y subtítulos)
solo funcionan si el contenedor de destino admite el códec. Las tablas recogen los
destinos que pyMedia considera **seguros** al cambiar de contenedor; si mantienes el
mismo contenedor de entrada, el margen es mayor.

### Vídeo

| Códec        | `.mkv` | `.mp4` | `.webm` |
|--------------|:------:|:------:|:-------:|
| `h264`       | ✓      | ✓      |         |
| `h265`       | ✓      | ✓      |         |
| `av1`        | ✓      | ✓      | ✓       |
| `vp9`        | ✓      |        | ✓       |
| `vp8`        | ✓      |        | ✓       |
| `mpeg4`      | ✓      | ✓      |         |
| `mpeg2video` | ✓      |        |         |
| `prores`     | ✓      |        |         |
| `dnxhd`      | ✓      |        |         |

### Audio

| Códec       | `.mkv` | `.mp4` | `.webm` | `.m4a` | `.mka` | `.ogg` | `.mp3` | `.flac` | `.ac3` |
|-------------|:------:|:------:|:-------:|:------:|:------:|:------:|:------:|:-------:|:------:|
| `aac`       | ✓      | ✓      |         | ✓      | ✓      |        |        |         |        |
| `ac3`       | ✓      |        |         |        | ✓      |        |        |         | ✓      |
| `eac3`      | ✓      | ✓      |         |        | ✓      |        |        |         |        |
| `opus`      | ✓      |        | ✓       |        | ✓      | ✓      |        |         |        |
| `vorbis`    | ✓      |        | ✓       |        | ✓      | ✓      |        |         |        |
| `mp3`       | ✓      |        |         |        | ✓      |        | ✓      |         |        |
| `flac`      | ✓      |        |         |        | ✓      | ✓      |        | ✓       |        |
| `alac`      | ✓      | ✓      |         | ✓      | ✓      |        |        |         |        |
| `truehd`    | ✓      |        |         |        | ✓      |        |        |         |        |
| `pcm_s16le` | ✓      |        |         |        |        |        |        |         |        |

### Subtítulos

| Códec                         | `.mkv` | `.mp4` | `.webm` | `.srt` | `.ass` | `.vtt` |
|-------------------------------|:------:|:------:|:-------:|:------:|:------:|:------:|
| `srt` (SubRip)                | ✓      |        |         | ✓      |        |        |
| `ass` / `ssa`                 | ✓      |        |         |        | ✓      |        |
| `webvtt`                      | ✓      |        | ✓       |        |        | ✓      |
| `mov_text`                    |        | ✓      |         |        |        |        |
| `dvd_subtitle` (VobSub)       | ✓      |        |         |        |        |        |
| `hdmv_pgs_subtitle` (PGS)     | ✓      |        |         |        |        |        |

Regla práctica: **MKV acepta casi todo**. Si una copia falla por compatibilidad,
prueba primero con `.mkv` (`.mka` para audio suelto).

Excepciones con subtítulos:

- `remux` a MP4 convierte siempre los subtítulos a `mov_text`.
- `transcode` avisa de las pistas que el contenedor de salida no admite y pregunta si
  convertir las de texto a su formato (`mov_text`, `srt` o `webvtt`). Las gráficas se
  descartan.

## Códecs de transcodificación

Los perfiles de `transcode` solo admiten estos códecs, elegidos por su eficiencia y
compatibilidad:

| Vídeo           | Codificador | Calidad (CRF) | Notas                                                         |
|-----------------|-------------|---------------|---------------------------------------------------------------|
| `h264`          | `libx264`   | 0–51          | Máxima compatibilidad (cualquier reproductor), 8 bits.        |
| `h265` / `hevc` | `libx265`   | 0–51          | Bastante menos tamaño que H.264 a igual calidad, 10 bits.        |
| `av1`           | `libsvtav1` | 0–63          | Mejor compresión, codificación más lenta, 10 bits.            |

| Audio  | Codificador | Tasas de bits                                   | Notas                                 |
|--------|-------------|-------------------------------------------------|---------------------------------------|
| `aac`  | `aac`       | 96k, 128k, 160k, 192k, 224k, 256k, 320k         | Compatibilidad universal.             |
| `eac3` | `eac3`      | 192k, 224k, 256k, 320k, 384k, 448k, 640k        | Dolby Digital Plus, sonido envolvente.|
| `opus` | `libopus`   | 64k, 96k, 128k, 160k, 192k, 256k                | Máxima eficiencia; no admitido en `.m4a`. |

Combinaciones de contenedor para el resultado de `transcode`:

| Contenedor | Vídeo admitido          | Audio admitido        |
|------------|-------------------------|-----------------------|
| `.mkv`     | `h264`, `h265`, `av1`   | `aac`, `eac3`, `opus` |
| `.mp4`     | `h264`, `h265`, `av1`   | `aac`, `eac3`, `opus` |
| `.webm`    | `av1`                   | `opus`                |

Como valor de `default_containers.media`, `.webm` solo es válido si **todos** los
perfiles usan AV1 y Opus, porque esa extensión debe servir para los tres (ver
[Configuración](configuracion.md#default_containers)).
