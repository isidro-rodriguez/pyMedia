Cli = {
    "concat_help": "Concatenates videos in the specified order",
    "crop_help": "Crops the specified number of pixels. [dim]E.g.: -c 200,200,0,0[/dim]",
    "debug_help": "Log level DEBUG",
    "encode_help": "Transcode using the selected options (requires at least one option)",
    "end_point_help": "Time point at which GIF generation ends. [dim]E.g.: -ep 1:20[/dim]",
    "fps_help": "Frames per second of the animated GIF. [dim]E.g.: -f 12[/dim]",
    "gif_help": "Generates an animated GIF from the specified video",
    "gyrate_help": "Rotate the media by the specified angle in degrees. [dim]E.g.: -g 90[/dim]",
    "invalid_path": "{path} is not a file.",
    "output_help": "Output file name. [dim]E.g.: -o cut.mp4[/dim]",
    "output_on_conflict_help": "Action to take if a file with the same name already exists. [dim]E.g.: -oc rename[/dim]",
    "path_argument_help": "Video to process.",
    "paths_argument_help": "Video list to process.",
    "remux_help": "Re-encodes using the profile specified in the configuration.",
    "scale_gif_help": "Resize the media proportionally to the specified height. [dim]E.g.: -s 240[/dim]",
    "scale_video_help": "Resize the media proportionally to the specified height. [dim]E.g.: -s 240[/dim]",
    "show_help": "Show this message and exit.",
    "split_help": "Splits a video at the specified points",
    "start_point_help": "Time point at which GIF generation starts. [dim]E.g.: -sp 1:20[/dim]",
    "trim_points_help": "Split points for the video. [dim]E.g.: -t 00:10,00:20,00:30[/dim]",
}


ConfigValidation = {
    "invalid_audio_bit_rate": "\nInvalid configuration setting: encode.audio_bit_rate is expected one of: {expected}",  # noqa: E501
    "invalid_audio_codec": "\nInvalid configuration setting: encode.audio_codec is expected one of: {expected}",  # noqa: E501
    "invalid_channels": "\nInvalid configuration setting: conflictive_join.channels is expected one of: {expected}",  # noqa: E501
    "invalid_default_container": "\nInvalid configuration setting: encode.default_container is expected one of: {expected}",  # noqa: E501
    "invalid_fps": "\nInvalid configuration setting: conflictive_join.fps is expected one of: {expected}",  # noqa: E501
    "invalid_language": "\nInvalid configuration setting: app.language is expected one of: {expected}",  # noqa: E501
    "invalid_resize_to": "\nInvalid configuration setting: conflictive_join.resize_to is expected one of: {expected}",  # noqa: E501
    "invalid_video_codec": "\nInvalid configuration setting: encode.video_codec is expected one of: {expected}",  # noqa: E501
    "invalid_video_crf": "\nInvalid configuration setting: encode.video_crf is expected between {min} and {max}",  # noqa: E501
    "invalid_video_preset": "\nInvalid configuration setting: encode.video_preset is expected one of: {expected}",  # noqa: E501
}


Debug = {
    "ffmpeg_command": "FFmpeg command: {cmd}",
    "ffprobe_data": "ffprobe data: {data}",
    "pipeline_crop": "Calculated crop: {crop}",
    "pipeline_gyrate": "Applied rotation: {gyrate}",
    "pipeline_scale": "Calculated scale: {scale}",
    "pipeline_time": "Processed time: {time}",
    "pipeline_trim": "Trim points: {trim}",
}


ExecutionError = {
    "cannot_create_directory": "Could not create directory: {path}",
    "command_execution": (
        "FFmpeg command '{command_name}' failed during execution. Error: {error}"
    ),
    "command_generation": "FFmpeg command '{command_name}' was not generated.",
    "ffmpeg_timeout": "FFmpeg operation exceeded the allowed timeout.",
    "invalid_config": "Invalid configuration: {message}",
    "invalid_config_setting": "Invalid configuration setting: {setting} is expected {expected}",  # noqa: E501
    "missing_config_section": "Missing configuration section: {section}",
    "missing_config_setting": "Missing configuration setting: {setting}",
    "unexpected_config_setting": "Unexpected configuration setting: {setting}",
}


Info = {
    "config_saved": "Saving config.toml",
    "concat_success": "Videos concatenated successfully: {output}",
    "encode_success": "Transcoding completed successfully: {output}",
    "gif_success": "GIF generated successfully: {output}",
    "split_success": "Video split successfully: {output}",
}


PipelineError = {
    "incompatible_files": "Video files are incompatible with each other.",
    "missing_arguments": "Missing arguments retrieved from Typer.",
    "missing_argument": "Missing argument: {argument}",
    "missing_media": "Media information for '{path}' could not be found.",
    "missing_media_property": "Media property '{property_name}' could not be found.",
    "output_on_conflict": "Stopped process because output file already exist.",
}


ValidationError = {
    "crop_all_zero": "Invalid crop: all values are 0.",
    "crop_exceeds_height": "Invalid crop: {total} >= original height {height}.",
    "crop_exceeds_width": "Invalid crop: {total} >= original width {width}.",
    "insufficient_inputs": "At least two videos must be provided for this command.",
    "invalid_crop_format": "Invalid crop format. Expected: LEFT,RIGHT,TOP,BOTTOM",
    "invalid_directory_name": (
        "'{directory}' contains invalid characters: '< > : \" / \\ | ? *'"
    ),
    "invalid_extension": "Invalid extension '{extension}'. Codec '{codec}' requires one of: {supported}",  # noqa: E501
    "invalid_filename": (
        "'{filename}' contains invalid characters: '< > : \" / \\ | ? *'"
    ),
    "invalid_gyrate": "Invalid rotation format. Expected: 90 | 180 | 270.",
    "invalid_time_format": "Invalid timestamp format. Expected: hh:mm:ss.",
    "invalid_trim_points": "Invalid trim points.",
    "missing_options": "At least one option is required.",
    "negative_time": "Timestamp cannot be negative.",
    "time_exceeds_duration": "Timestamp {time} exceeds video duration {duration}.",
}


Warnings = {
    "missing_options": "At least one option is required.",
    "output_exist": "File already exist: {file_path}",
    "scale_rejected_equal": "Scaling rejected: {scale} = original height {height}.",
    "scale_rejected_increase": (
        "Scaling to {scale}p not applied: resolution is higher than the original "
        "({height}p)."
    ),
}
