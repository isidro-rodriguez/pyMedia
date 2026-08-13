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

Info = {
    "config_saved": "Saving config.toml",
    "concat_success": "Videos concatenated successfully: {output}",
    "encode_success": "Transcoding completed successfully: {output}",
    "gif_success": "GIF generated successfully: {output}",
    "split_success": "Video split successfully: {output}",
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
