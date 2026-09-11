# pyMedia

Aplicación CLI que actúa como handler sencillo de comandos `ffmpeg` para tareas habituales de 
procesamiento de vídeos.

> Estado: **Alpha** (en pruebas locales).

## Requisitos

**Ffmpeg** y **ffprobe** instalados y disponibles en el `PATH`.
    
- Windows: `winget install ffmpeg` o <https://ffmpeg.org/download.html>
- Debian/Ubuntu: `sudo apt install ffmpeg`

## Comandos de pyMedia

| Comando     | Acción                                                         |
| ----------- | -------------------------------------------------------------- |
| `info`      | Muestra metadatos del archivo multimedia.                      |
| `sheet`     | Genera una imagen con múltiples fotogramas en cuadrícula.      |
| `join`      | Une varios vídeos consecutivamente.                            |
| `remux`     | Cambia contenedor y metadatos sin transcodificar.              |
| `split`     | Divide un vídeo en varios archivos.                            |
| `transcode` | Transcodifica el contenedor cambiando códecs de vídeo o audio. |
| `audio`     | Familia de comandos de modificación de pistas de audio.        |
| `subs`      | Familia de comandos de modificación de pistas de subtítulos.   |
| `thumb`     | Familia de comandos de capturas de imágenes.                   |
| `animated`  | Convierte un fragmento de vídeo en imagen animada.             |

## Configuración

### Compatibilidad entre códecs y contenedores de vídeo

|        | AV1 | H.264 | H.265 | AAC | E-AC-3 | Opus | ASS | SRT | SSA |
|--------|:---:|:-----:|:-----:|:---:|:------:|:----:|:---:|:---:|:---:|
| MKV    | ✓  |  ✓   |  ✓   | ✓  |   ✓   |  ✓  | ✓  | ✓  | ✓  |
| MP4    | ✓  |  ✓   |  ✓   | ✓  |   ✓   |      |     | ⚠  |     |
| WebM   | ✓  |       |       |     |        |  ✓  |     |     |     |

> ⚠ = Se transcodifica a `mov_text`

### Compatibilidad entre códecs y contenedores de audio

|     | AAC | ALAC | FLAC | Opus | MP3 |
|-----|:---:|:----:|:----:|:----:|:---:|
| MKA | ✓  |  ✓  |  ✓  |  ✓  | ✓  |
| M4A | ✓  |  ✓  |      |  ⚠  |     |
| OGG |     |      |  ✓  |  ✓  | ⚠  |

> ⚠ = Soporte parcial/no universal, evitar si buscas compatibilidad amplia.

### Perfiles de transcodificación comunes

| Perfil       | Vídeo | CRF |  Preset  | Audio | Bit rate | Contenedor |
|:-------------|:-----:|:---:|:--------:|:------|---------:|:----------:|
| **fast**     | H264  | 21  | veryfast | AAC   | 192 kb/s |    MP4     |
| **balanced** | H265  | 22  |  medium  | Opus  | 112 kb/s |    MKV     |
| **slow**     |  AV1  | 24  |    7     | Opus  |  96 kb/s |    MKV     |

