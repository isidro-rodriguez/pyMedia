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
