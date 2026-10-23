# Comandos de imagen

Los cuatro comandos aceptan los [filtros de imagen](../filtros.md) (`--crop`, `--size`,
`--mode`, `--upscale`, `--rotate`, `--hflip`, `--vflip`).

| Comando    | Resultado                                            | Selección de fotogramas              |
|------------|------------------------------------------------------|--------------------------------------|
| `animated` | Una imagen animada (`.gif`, `.apng`, `.webp`).       | Tramo `--start`/`--end` a `--fps`.   |
| `frames`   | Una imagen por marca.                                | Marcas exactas `--at`.               |
| `interval` | Una imagen cada N segundos.                          | `--every`, opcional `--start`/`--end`. |
| `scene`    | Una imagen por cambio de plano.                      | Umbral `--scene`, opcional `--start`/`--end`. |

## Formatos de imagen fija

`frames`, `interval`, `scene` y `sheet` escriben en el formato que indique la extensión
de salida (por defecto `default_containers.image`, `.jpg`):

| Extensión        | Codificación                                   | Uso recomendado               |
|------------------|------------------------------------------------|-------------------------------|
| `.jpg`, `.jpeg`  | MJPEG, calidad alta (`-q:v 2`), rango completo | Fotografía, tamaño reducido.  |
| `.png`           | Sin pérdida, RGB                               | Capturas nítidas, edición.    |
| `.webp`          | `libwebp`                                      | Web, buen equilibrio.         |

## `animated`

Convierte un tramo de vídeo en una imagen animada.

```bash
pymedia animated video.mp4                                  # vídeo completo
pymedia animated video.mp4 --start 00:00:05 --end 00:00:12
pymedia animated video.mp4 --size 480x270 --fps 15 -o clip.webp
```

| Opción       | Valores         | Defecto                         | Descripción                        |
|--------------|-----------------|---------------------------------|------------------------------------|
| `--start`    | Marca de tiempo | Inicio                          | Comienzo del tramo.                |
| `--end`      | Marca de tiempo | Final                           | Fin del tramo.                     |
| `--fps`      | 4–20            | 12                              | Fotogramas por segundo.            |
| `--size`     | `ANCHOxALTO`    | `640x360`                       | Tamaño máximo (modo `fit`).        |
| `-o`         | `.gif`, `.apng`, `.webp` | `<nombre>.<animated_image>` | Fichero de salida.          |

- GIF y APNG generan una paleta optimizada de 256 colores para el tramo y aplican
  _dithering_, lo que mejora mucho la calidad frente a la conversión directa.
- WebP admite color completo y suele ocupar menos que GIF.
- El tamaño final crece con la duración, el tamaño y los fps: para compartir,
  mantén el tramo corto (5–10 s) y `--fps` entre 10 y 15.

## `frames`

Captura un fotograma en cada marca de tiempo indicada.

```bash
pymedia frames video.mp4 --at 00:01:30
pymedia frames video.mp4 --at 00:01:30,00:05:15 -o portada.png
```

| Opción | Descripción                                   |
|--------|-----------------------------------------------|
| `--at` | Marcas de tiempo, separadas por comas.        |
| `-o`   | Nombre base; se añade la marca a cada fichero. |

Para evitar fotogramas borrosos o de transición, pyMedia analiza los 30 fotogramas
siguientes a cada marca y elige el más representativo (filtro `thumbnail`). La imagen
puede corresponder, por tanto, a un instante ligeramente posterior.

Cada captura se guarda como `<nombre>_thumbnail_<h-mm-ss>.<ext>`.

## `interval`

Captura fotogramas a intervalos regulares.

```bash
pymedia interval video.mp4 --every 60
pymedia interval video.mp4 --every 5 --start 00:00:10 --end 00:01:00 -o capturas/clip.png
```

| Opción    | Descripción                                  |
|-----------|----------------------------------------------|
| `--every` | Intervalo en segundos entre capturas.        |
| `--start` | Comienzo del tramo (opcional).               |
| `--end`   | Fin del tramo (opcional).                    |

Las capturas se numeran: `<nombre>_thumbnail_001.jpg`, `_002`… Como en `frames`,
cada captura se elige entre fotogramas cercanos para evitar imágenes borrosas.

## `scene`

Captura un fotograma cada vez que la imagen cambia de forma significativa, por ejemplo
en un cambio de plano.

```bash
pymedia scene video.mp4
pymedia scene video.mp4 --scene 0.4 --start 00:00:05 --end 00:00:30
```

| Opción    | Valores   | Defecto | Descripción                                          |
|-----------|-----------|---------|------------------------------------------------------|
| `--scene` | 0.1–0.5   | 0.3     | Umbral de cambio entre fotogramas consecutivos.      |
| `--start` | Marca     | Inicio  | Comienzo del tramo.                                  |
| `--end`   | Marca     | Final   | Fin del tramo.                                       |

- Un umbral **bajo** (0.1) detecta cambios sutiles y genera muchas capturas.
- Un umbral **alto** (0.5) solo detecta cortes muy marcados.
- Empieza con el valor por defecto y ajusta según el resultado.

Las capturas se numeran: `<nombre>_thumbnail_001.jpg`, `_002`…
