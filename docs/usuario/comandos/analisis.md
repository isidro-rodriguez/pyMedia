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
