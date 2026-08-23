Cli = {
    "debug_help": "Log level DEBUG",
    "end_point_help": "Time point at which GIF generation ends.",
    "fps_help": "Frames per second of the animated GIF.",
    "gif_help": "Generates an animated GIF from the specified video",
    "invalid_path": "{path} is not a file.",
    "output_help": "Output file name.",
    "overwrite_confirm": "Output file already exists. Overwrite?",
    "overwrite_help": "Action to use if output file already exists.",
    "path_argument_help": "Video to process.",
    "scale_help": "Resize proportionally to the specified height.",
    "show_help": "Show this message and exit.",
    "start_point_help": "Time point at which GIF generation starts.",
}


ConfigValidation = {
    "invalid_audio_bit_rate": "\nInvalid configuration setting: encode.audio_bit_rate is expected one of: {expected}.",
    "invalid_audio_codec": "\nInvalid configuration setting: encode.audio_codec is expected one of: {expected}.",
    "invalid_channels": "\nInvalid configuration setting: conflictive_concat.channels is expected one of: {expected}.",
    "invalid_default_container": "\nInvalid configuration setting: encode.default_container is expected one of: {expected}.",
    "invalid_fps": "\nInvalid configuration setting: conflictive_concat.fps is expected one of: {expected}.",
    "invalid_language": "\nInvalid configuration setting: app.language is expected one of: {expected}.",
    "invalid_stall_timeout": "\nInvalid configuration setting: app.stall_timeout is expected to an integer between 30 to 600.",
    "invalid_video_codec": "\nInvalid configuration setting: encode.video_codec is expected one of: {expected}.",
    "invalid_video_crf": "\nInvalid configuration setting: encode.video_crf is expected between {min} and {max}.",
    "invalid_video_preset": "\nInvalid configuration setting: encode.video_preset is expected one of: {expected}.",
}


Debug = {
    "ffmpeg_command": "FFmpeg command: {cmd}",
    "ffprobe_data": "ffprobe data: {data}",
}


ExecutionError = {
    "cannot_create_directory": "Could not create directory: {path}",
    "command_execution": "FFmpeg command {command_name} failed during execution. Error: {error}",
    "command_generation": "FFmpeg command {command_name} was not generated.",
    "command_timeout": "FFmpeg command {command_name} timed out.",
    "invalid_config": "Invalid configuration: {message}",
}


Info = {
    "gif_success": "GIF generated successfully: {output}",
}


ParameterError = {
    "missing_argument": "Missing argument: {argument}",
    "missing_media": "Missing media information: {path}",
    "missing_media_property": "Missing media property: {property_name}",
}


Progress = {
    "gif": "Generating GIF",
}


ValidationError = {
    "crop_exceeds_dimensions": "Invalid crop dimensions: {crop_dimensions} >= original {video_dimensions}.",
    "invalid_borders_format": "Invalid borders format. Expected: LEFT,RIGHT,TOP,BOTTOM.",
    "invalid_crop_format": "Invalid crop format. Expected: WIDTH,HEIGHT,X,Y.",
    "invalid_directory_name": '{directory} contains invalid characters: < > : " / \\ | ? *',
    "invalid_extension": "Invalid extension {extension}. Codec {codec} requires one of: {supported}.",
    "invalid_filename": '{filename} contains invalid characters: < > : " / \\ | ? *',
    "invalid_output_extension": "Invalid extension {extension}. Requires one of: {supported}.",
    "invalid_time_format": "Invalid timestamp format. Expected: hh:mm:ss.",
    "time_exceeds_duration": "Timestamp {time} exceeds video duration {duration}.",
}


Warnings = {
    "overwrite_skipped": "Command skipped since output file already exists.",
    "scale_rejected_equal": "Scaling rejected: {scale} = original height {height}.",
    "scale_rejected_increase": "Scaling to {scale}p not applied: resolution is higher than the original ({height}p).",
}
