"""Script que encadena la generación de fixtures de prueba.

El orden importa: los vídeos reutilizan las pistas de audio y subtítulos.
"""

from fixtures.audio_tracks import main as generate_audio_tracks
from fixtures.subtitle_tracks import main as generate_subtitles_tracks
from fixtures.video_files import main as generate_video_files


def main() -> None:
    """Genera la lista de fixtures disponibles."""
    generate_audio_tracks()
    generate_subtitles_tracks()
    generate_video_files()


if __name__ == "__main__":
    main()
