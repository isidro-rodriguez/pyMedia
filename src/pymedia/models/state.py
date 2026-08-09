import subprocess
from dataclasses import dataclass, field
from json import JSONDecodeError
from pathlib import Path

from pymedia.logger import get_logger
from pymedia.models.arguments import Arguments
from pymedia.models.config import Config
from pymedia.models.gif_pipeline import GifPipeline
from pymedia.models.media import Media
from pymedia.models.video_pipeline import VideoPipeline
from pymedia.services.basename_service import process_inputs, process_output
from pymedia.services.pipeline_service import (
    process_crop,
    process_gyrate,
    process_scale,
    process_time,
    process_trim_points,
)

logger = get_logger("state")


@dataclass
class State:
    config: Config
    arguments: Arguments | None = None
    inputs: list[Path] = field(default_factory=list)
    output: Path | None = None
    media: list[Media] = field(default_factory=list)
    video_pipeline: VideoPipeline | None = None
    gif_pipeline: GifPipeline | None = None

    def set_inputs(self, inputs: list[Path]) -> None:
        """Comprueba que la extensión del vídeo de entrada sea válida."""
        self.inputs = process_inputs(inputs)

    def set_output(self, output: Path) -> None:
        """Comprueba el fichero de salida tenga un nombre y extensión válido."""
        self.output = process_output(self, output)

    def set_media(self, paths: list[Path]) -> None:
        for p in paths:
            try:
                media: Media = Media.load(p)
            except (
                ValueError,
                subprocess.CalledProcessError,
                JSONDecodeError,
                OSError,
            ):
                logger.error(f"Vídeo con formato inválido: {p}")
                raise

            self.media.append(media)

    def set_arguments(self, args: Arguments) -> None:
        self.arguments = args

    def set_video_pipeline(self) -> None:
        if self.arguments is None:
            raise RuntimeError(
                "Argumentos de comando no recogidos antes de construir el pipeline"
            )

        args: Arguments = self.arguments
        self.video_pipeline = VideoPipeline.load()

        if args.crop is not None:
            self.video_pipeline.crop = process_crop(self)

        if args.gyrate is not None:
            self.video_pipeline.gyrate = process_gyrate(self)

        self.video_pipeline.remux = args.remux

        if args.scale:
            self.video_pipeline.scale = process_scale(self)

        if args.trim_points:
            self.video_pipeline.trim_points = process_trim_points(self)

    def set_gif_pipeline(self) -> None:
        if self.arguments is None:
            raise RuntimeError(
                "Argumentos de comando no recogidos antes de construir el pipeline"
            )

        args: Arguments = self.arguments

        self.gif_pipeline = GifPipeline.load()

        if args.crop is not None:
            self.gif_pipeline.crop = process_crop(self)

        if args.end_point is not None:
            self.gif_pipeline.end_point = process_time(self, args.end_point)

        if args.fps is not None:
            self.gif_pipeline.fps = args.fps

        if args.gyrate is not None:
            self.gif_pipeline.gyrate = process_gyrate(self)

        if args.scale:
            self.gif_pipeline.scale = process_scale(self)

        if args.start_point:
            self.gif_pipeline.start_point = process_time(self, args.start_point)


state = State(config=Config.load())
