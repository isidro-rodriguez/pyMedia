# Comandos de audio

Todos los comandos de audio copian las pistas sin recodificar (`-c copy`). Los índices
de pista son los que muestra `info` (ver [Pistas e índices](../conceptos.md#pistas-e-índices)).

## `add-audio`

Añade al vídeo las pistas de audio de otro fichero.

```bash
pymedia add-audio pelicula.mkv doblaje.m4a
pymedia add-audio pelicula.mkv doblaje.m4a -o pelicula_dual.mkv
```

| Argumento / opción    | Descripción                                                 |
|-----------------------|-------------------------------------------------------------|
| `MEDIA_FILE`          | Vídeo de destino.                                           |
| `AUDIO_FILE`          | Fichero con las pistas de audio que añadir.                 |
| `--strip-disposition` | No copia los metadatos del origen.       |
| `-o`, `-ov`           | Ver [opciones comunes](../conceptos.md#opciones-comunes).   |

- Se añaden **todas** las pistas de audio del fichero, al final de las existentes.
- El fichero de audio se analiza con ffprobe. Si contiene vídeo o subtítulos, se
  muestra un aviso y solo se toma el audio.
- Idioma y título se heredan del fichero de audio.
- Si el vídeo ya tenía audio, las pistas importadas llegan **sin disposiciones**
  (ni predeterminada ni forzada) para no crear dos pistas predeterminadas. Ajústalas
  después con `edit-audio`.
- El códec del audio debe poder copiarse al contenedor del vídeo (por ejemplo, Opus
  no se admite en `.m4a`). Ver [Formatos](../formatos.md).

## `delete-audio`

Elimina pistas de audio.

```bash
pymedia delete-audio pelicula.mkv --tracks 1,2
```

| Opción      | Descripción                                           |
|-------------|-------------------------------------------------------|
| `--tracks`  | **Obligatorio.** Índices de las pistas que eliminar.  |
| `-o`, `-ov` | Ver [opciones comunes](../conceptos.md#opciones-comunes). |

El resto de pistas (vídeo, audio y subtítulos) se copian intactas.

## `edit-audio`

Cambia los metadatos y las disposiciones de una pista de audio.

```bash
pymedia edit-audio pelicula.mkv --track 1 --language spa
pymedia edit-audio pelicula.mkv --track 1 --language spa --title "Comentario" --commentary
pymedia edit-audio pelicula.mkv --track 0 --default
pymedia edit-audio pelicula.mkv --track 2 --no-forced
```

| Opción                                      | Descripción                                                  |
|---------------------------------------------|--------------------------------------------------------------|
| `--track`                                   | **Obligatorio.** Índice de la pista.                         |
| `--language`                                | Idioma (ver abajo).                                          |
| `--title`                                   | Título visible en el reproductor.                            |
| `--default` / `--no-default`                | Pista predeterminada del contenedor.                         |
| `--forced` / `--no-forced`                  | Pista forzada.                                               |
| `--hearing-impaired` / `--no-hearing-impaired` | Destinada a personas con discapacidad auditiva.           |
| `--commentary` / `--no-commentary`          | Pista de comentarios.                                        |
| `-o`, `-ov`                                 | Ver [opciones comunes](../conceptos.md#opciones-comunes).    |

- Las disposiciones que no indiques se conservan. Cada flag tiene su forma `--no-`
  para quitarla.
- `--default` es **exclusivo**: al marcar una pista como predeterminada, el resto de
  pistas de audio pierden esa marca.
- `--language` acepta un código ISO 639-1 (`es`), ISO 639-2 (`spa`), el nombre en
  inglés (`Spanish`) o el nombre nativo (`Español`). Se guarda siempre como ISO 639-2.
- Si indicas `--language` sin `--title` y la pista no tenía título, se usa el nombre
  nativo del idioma como título.

## `extract-audio`

Extrae pistas de audio a ficheros independientes, sin recodificar.

```bash
pymedia extract-audio pelicula.mkv --tracks 0
pymedia extract-audio pelicula.mkv --tracks 1,2 -o audio.mka
```

| Opción                | Descripción                                              |
|-----------------------|----------------------------------------------------------|
| `--tracks`            | **Obligatorio.** Índices de las pistas que extraer.      |
| `--strip-disposition` | No copia los metadatos del origen.                     |
| `-o`, `-ov`           | Ver [opciones comunes](../conceptos.md#opciones-comunes). |

- Se genera un fichero por pista: `<nombre>_audio_track_<N>.<ext>`.
- La extensión por defecto es `default_containers.audio_track` (`.m4a`). Debe admitir
  el códec de cada pista: para AC-3, Opus o FLAC usa `-o audio.mka`, el contenedor
  más flexible.
