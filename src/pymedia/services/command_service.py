from pathlib import Path

from pymedia.cli_params import OutputOnConflictMode
from pymedia.errors import OutputOnConflictError
from pymedia.logger import log_warning
from pymedia.models.arguments import Arguments, CommandName
from pymedia.models.state import state


def initialize_command(args: Arguments) -> None:
    state.set_arguments(args)
    state.set_inputs(args.inputs)
    state.set_media(args.inputs)
    if args.output is not None:
        state.set_output(args.output)
    if args.command is CommandName.GIF:
        state.set_gif_pipeline()
    else:
        state.set_video_pipeline()
    state.set_output_on_conflict()


def _get_available_output_path(output: Path) -> Path:
    candidate = output
    index = 1

    while candidate.exists():
        candidate = output.with_stem(f"{output.stem}_{index}")
        index += 1

    return candidate


def resolve_output_conflict(output: Path, logger) -> Path | None:
    if not output.exists():
        return output

    log_warning(logger, "output_exist", file_path=output)

    match state.output_on_conflict:
        case OutputOnConflictMode.FAIL:
            raise OutputOnConflictError()

        case OutputOnConflictMode.RENAME:
            return _get_available_output_path(output)

        case OutputOnConflictMode.REPLACE:
            return output

        case OutputOnConflictMode.SKIP:
            return None

    return None
