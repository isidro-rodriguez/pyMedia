"""Genera un vídeo de prueba con un fractal de Mandelbrot animado y audio tonal."""

#!/usr/bin/env python3

import subprocess

# ============================================================
# CONFIGURACIÓN
# ============================================================
CONFIG = {
    # Archivo de salida
    "output": "simple.mp4",
    # Vídeo
    "width": 1280,
    "height": 720,
    "fps": 30,
    "duration": 30,
    # AV1 / SVT-AV1
    # CRF más bajo = mayor calidad / archivo más grande
    "video_codec": "libsvtav1",
    "video_crf": 30,
    "video_preset": 8,
    # Fractal Mandelbrot
    "fractal_start": "0.001",
    "fractal_end": "0.001",
    "fractal_maxiter": 200,
    # Audio
    "audio_codec": "aac",
    "audio_bitrate": "128k",
    "audio_frequency": 440,
    "audio_sample_rate": 48000,
}


def build_ffmpeg_command(config):
    """Construye el comando ffmpeg a partir de la configuración indicada.

    Args:
        config: Diccionario con los parámetros de generación del vídeo.

    Returns:
        Lista con el comando ffmpeg listo para ejecutar.
    """
    width = config["width"]
    height = config["height"]
    fps = config["fps"]
    duration = config["duration"]

    # --------------------------------------------------------
    # Fractal
    #
    # Generamos Mandelbrot directamente con FFmpeg.
    #
    # size:
    #     Resolución final.
    #
    # rate:
    #     Número de frames por segundo.
    #
    # maxiter:
    #     Número máximo de iteraciones del fractal.
    #     Valores mayores producen más detalle, pero consumen
    #     más CPU.
    # --------------------------------------------------------
    fractal = (
        f"mandelbrot="
        f"size={width}x{height}:"
        f"rate={fps}:"
        f"maxiter={config['fractal_maxiter']}"
    )

    # --------------------------------------------------------
    # Zoom suave.
    #
    # zoompan genera una animación continua sobre el fractal.
    # La expresión aumenta ligeramente el zoom con el tiempo.
    #
    # 'on' = número de frame generado.
    # --------------------------------------------------------
    zoom = (
        f"zoompan="
        f"z='min(zoom+0.0015,2.5)':"
        f"x='iw/2-(iw/zoom/2)':"
        f"y='ih/2-(ih/zoom/2)':"
        f"d=1:"
        f"s={width}x{height}:"
        f"fps={fps}"
    )

    video_filter = f"{fractal},{zoom},trim=duration={duration},setpts=PTS-STARTPTS"

    # --------------------------------------------------------
    # Audio:
    # tono sinusoidal sencillo de duración exacta.
    # --------------------------------------------------------
    audio_filter = (
        f"sine="
        f"frequency={config['audio_frequency']}:"
        f"sample_rate={config['audio_sample_rate']}:"
        f"duration={duration}"
    )

    command = [
        "ffmpeg",
        "-y",
        # ----------------------------------------------------
        # Entrada de vídeo: filtro fractal de FFmpeg
        # ----------------------------------------------------
        "-f",
        "lavfi",
        "-i",
        video_filter,
        # ----------------------------------------------------
        # Entrada de audio: tono sinusoidal
        # ----------------------------------------------------
        "-f",
        "lavfi",
        "-i",
        audio_filter,
        # ----------------------------------------------------
        # Vídeo AV1
        # ----------------------------------------------------
        "-c:v",
        config["video_codec"],
        "-crf",
        str(config["video_crf"]),
        "-preset",
        str(config["video_preset"]),
        # ----------------------------------------------------
        # Audio AAC
        # ----------------------------------------------------
        "-c:a",
        config["audio_codec"],
        "-b:a",
        config["audio_bitrate"],
        # Duración exacta
        "-t",
        str(duration),
        # Permite reproducir el MP4 progresivamente
        "-movflags",
        "+faststart",
        config["output"],
    ]

    return command


def main():
    """Genera el vídeo de prueba ejecutando ffmpeg."""
    command = build_ffmpeg_command(CONFIG)

    print("Ejecutando FFmpeg:\n")
    print(" ".join(command))
    print()

    subprocess.run(command, check=True)

    print()
    print(f"Vídeo generado: {CONFIG['output']}")


if __name__ == "__main__":
    main()
