# Comandos de análisis

## `info`

Muestra los metadatos de un fichero de vídeo en un panel con una tabla por tipo de pista.

```bash
pymedia info pelicula.mkv
```

| Sección     | Datos                                                                                |
|-------------|--------------------------------------------------------------------------------------|
| General     | Nombre, contenedor, duración, tamaño, metadatos globales (título, fecha, género, artista, codificador…). |
| Vídeo       | Índice, códec y perfil, resolución, fps y tasa de bits.                              |
| Audio       | Índice, códec, frecuencia de muestreo, canales, idioma, título y disposiciones.      |
| Subtítulos  | Índice, códec, idioma, título y disposiciones.                                       |

Las columnas de disposición se abrevian: `Def` (predeterminada), `For` (forzada),
`HI` (discapacidad auditiva), `Com` (comentario) y `VI` (discapacidad visual).

La columna **Track** es el índice que aceptan `--track` y `--tracks` en el resto de
comandos (ver [Pistas e índices](../conceptos.md#pistas-e-índices)).

Si ffprobe no declara la tasa de bits del vídeo, pyMedia la estima a partir del
tamaño y la duración del contenedor. La estimación incluye el audio, así que es una
cota superior.

| Opción     | Descripción              |
|------------|--------------------------|
| `--debug`  | Muestra el JSON completo de ffprobe. |

## `sheet`

Genera una hoja de contactos: una cuadrícula de miniaturas con la marca de tiempo de
cada una y una cabecera con los metadatos del vídeo.

```bash
pymedia sheet pelicula.mkv
pymedia sheet pelicula.mkv --preset fhd -o hoja.webp
pymedia sheet *.mp4 --preset web -d hojas/
```

| Opción              | Valores            | Defecto | Descripción                                   |
|---------------------|--------------------|---------|-----------------------------------------------|
| `--preset`          | `fhd`, `hd`, `web` | `hd`    | Estilo y tamaño de la hoja.                   |
| `-o`, `--output`    | Ruta               | `<nombre>_sheet.<image>` | Fichero de salida (`.jpg`, `.jpeg`, `.png`, `.webp`). |
| `-d`, `--directory` | Ruta               | —       | Directorio de salida para varios vídeos.      |
| `-ov`, `--overwrite`| `yes`, `no`, `ask` | `ask`   | Política de sobrescritura.                    |

### Preajustes

| Preajuste | Ancho   | Cuadrícula | Miniaturas | Tamaño de fuente (cabecera / marca) |
|-----------|---------|------------|------------|-------------------------------------|
| `fhd`     | 1920 px | 5 × 4      | 20         | 22 / 15                             |
| `hd`      | 1280 px | 4 × 3      | 12         | 14 / 12                             |
| `web`     | 800 px  | 3 × 3      | 9          | 12 / 11                             |

### Funcionamiento

1. Las miniaturas se reparten uniformemente entre el 5 % y el 95 % de la duración,
   para evitar créditos y pantallas en negro.
2. ffmpeg compone la cuadrícula en un fichero temporal en una sola pasada.
3. Una segunda pasada añade la cabecera con nombre, tamaño, duración, datos de vídeo
   (resolución, códec, formato de píxel, fps y tasa de bits) y un resumen de las
   pistas de audio y subtítulos. Las listas largas se recortan con `...` para no
   superar el ancho de la hoja.

La tipografía (Source Code Pro Bold) se copia a `assets/`, dentro del directorio de
configuración del usuario, la primera vez que se usa.

## `play`

Reproduce un vídeo con `ffplay` en una ventana. Sirve para revisar un fichero o para
**previsualizar** un tramo, una pista o unos filtros de imagen antes de procesarlo
con `cut` o `transcode`. No escribe ningún fichero.

```bash
pymedia play pelicula.mkv
pymedia play pelicula.mkv --start 10:00 --end 12:30 --audio 1 --subs 0
pymedia play pelicula.mp4 --crop 1280,720,0,140 --size 960x540
pymedia play pelicula.mp4 --burn-subtitles subs.srt --volume 50
```

| Opción              | ffplay            | Descripción                                                         |
|---------------------|-------------------|---------------------------------------------------------------------|
| `--start`, `--end`  | `-ss`, `-t`       | Tramo a reproducir. El final se convierte en duración desde el inicio. |
| `--audio N`         | `-ast a:N`        | Pista de audio a reproducir (índice de `info`).                     |
| `--subs N`          | `-sst s:N`        | Pista de subtítulos a mostrar.                                      |
| `--no-subs`         | `-sn`             | Oculta los subtítulos del contenedor.                               |
| `--burn-subtitles`  | `-vf subtitles=`  | Dibuja un fichero `.srt`/`.ass`/`.ssa` sobre el vídeo y oculta los internos. |
| `--mute`            | `-an`             | Reproduce sin audio.                                                |
| `--volume`          | `-volume`         | Volumen inicial, de 0 a 100.                                        |
| `--loop`            | `-loop 0`         | Repite hasta cerrar la ventana; con `--start`/`--end`, repite el tramo. |
| `--fullscreen`      | `-fs`             | Abre a pantalla completa.                                           |
| `--crop`, `--size`, `--mode`, `--upscale`, `--rotate`, `--hflip`, `--vflip` | `-vf` | Los mismos [filtros de imagen](../filtros.md) que `transcode`. |

No se pueden combinar `--mute` con `--audio`, ni `--subs`, `--no-subs` y
`--burn-subtitles` entre sí.

### Controles de ffplay

| Tecla           | Acción                           |
|-----------------|----------------------------------|
| ++space++       | Pausa / continúa.                |
| ++left++ / ++right++ | Retrocede / avanza 10 s.    |
| ++down++ / ++up++    | Retrocede / avanza 1 min.   |
| ++9++ / ++0++   | Baja / sube el volumen.          |
| ++m++           | Silencio.                        |
| ++a++ / ++t++   | Siguiente pista de audio / de subtítulos. |
| ++f++           | Pantalla completa.               |
| ++q++ / ++esc++ | Cierra la ventana.               |

!!! note "ffplay"
    `play` es el único comando que necesita `ffplay`, y solo lo comprueba al
    ejecutarse: el resto de comandos funcionan aunque no esté instalado. Viene con el
    paquete `ffmpeg` de Debian/Ubuntu, con `winget install ffmpeg` y con Homebrew.
    `--show-cmd` muestra el comando aunque ffplay no esté instalado.

La ventana no se cierra sola al terminar el vídeo: ciérrala con ++q++. La salida de
ffplay (estado de reproducción y errores) se muestra directamente en la terminal.
