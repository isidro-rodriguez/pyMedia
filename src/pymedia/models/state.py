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
        from pymedia.services.basename_service import process_inputs

        self.inputs = process_inputs(inputs)

    def set_output(self, output: Path) -> None:
        """Comprueba el fichero de salida tenga un nombre y extensión válido."""
        from pymedia.services.basename_service import process_output

        pipeline = self.video_pipeline
        requires_encode = pipeline.requires_encode if pipeline else False

        if requires_encode:
            target_codec = self.config.encode.video_codec
        else:
            video = self.media[0].video if self.media else None
            target_codec = video.codec if video else None

        self.output = process_output(
            output=output,
            target_codec=target_codec,
            is_gif=self.gif_pipeline is not None,
        )

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

        from pymedia.services.pipeline_service import (
            process_crop,
            process_gyrate,
            process_scale,
            process_trim_points,
        )

        args: Arguments = self.arguments
        self.video_pipeline = VideoPipeline.load()

        if args.crop is not None:
            self.video_pipeline.crop = process_crop(args.crop, self.media)

        if args.gyrate is not None:
            self.video_pipeline.gyrate = process_gyrate(args.gyrate)

        self.video_pipeline.remux = args.remux

        if args.scale:
            self.video_pipeline.scale = process_scale(
                args.scale,
                self.media,
                self.config.app.disable_resolution_increase,
            )

        if args.trim_points:
            duration = self.media[0].duration if self.media else None
            input_path = self.inputs[0] if self.inputs else Path()
            self.video_pipeline.trim_points = process_trim_points(
                args.trim_points,
                duration,
                input_path,
            )

    def set_gif_pipeline(self) -> None:
        if self.arguments is None:
            raise RuntimeError(
                "Argumentos de comando no recogidos antes de construir el pipeline"
            )

        from pymedia.services.pipeline_service import (
            process_crop,
            process_gyrate,
            process_scale,
            process_time,
        )

        args: Arguments = self.arguments

        self.gif_pipeline = GifPipeline.load()

        if args.crop is not None:
            self.gif_pipeline.crop = process_crop(args.crop, self.media)

        if args.end_point is not None:
            duration = self.media[0].duration if self.media else None
            self.gif_pipeline.end_point = process_time(args.end_point, duration)

        if args.fps is not None:
            self.gif_pipeline.fps = args.fps

        if args.gyrate is not None:
            self.gif_pipeline.gyrate = process_gyrate(args.gyrate)

        if args.scale:
            self.gif_pipeline.scale = process_scale(
                args.scale,
                self.media,
                self.config.app.disable_resolution_increase,
            )

        if args.start_point:
            duration = self.media[0].duration if self.media else None
            self.gif_pipeline.start_point = process_time(args.start_point, duration)


state = State(config=Config.load())
