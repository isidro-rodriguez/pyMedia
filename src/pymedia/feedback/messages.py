ExecutionError = {
    "command_execution": (
        "FFmpeg command '{command_name}' failed during execution. Error: {error}"
    ),
    "command_generation": "FFmpeg command '{command_name}' was not generated.",
    "ffmpeg_timeout": "FFmpeg operation exceeded the allowed timeout.",
    "cannot_create_directory": "No se pudo crear el directorio: {path}",
    "invalid_config": "Configuración inválida: {message}",
}

PipelineError = {
    "missing_media": "Media information of '{path}' could not be found.",
    "missing_media_property": "'{property_name}' media information could not be found.",
    "incompatible_files": "Video files are incompatible with each other.",
}

ValidationError = {
    "invalid_directory_name": (
        "'{directory}' contiene caracteres no válidos: '< > : \" / \\ | ? *'"
    ),
    "invalid_filename": (
        "'{filename}' contiene caracteres no válidos: '< > : \" / \\ | ? *'"
    ),
    "invalid_extension": (
        "Extensión '{extension}' no válida. Tiene que ser: {supported}"
    ),
    "invalid_crop_format": "Formato de crop inválido. Esperado: IZQ,DER,ARRIBA,ABAJO",
    "crop_all_zero": "Crop inválido: todos los valores son 0.",
    "crop_exceeds_width": "Crop inválido: {total} >= ancho original {width}.",
    "crop_exceeds_height": "Crop inválido: {total} >= alto original {height}.",
    "invalid_gyrate": "Formato de giro no valido. Esperado 90 | 180 | 270.",
    "invalid_time_format": "Formato de marca de tiempo no válida. Esperado hh:mm:ss.",
    "negative_time": "Marca de tiempo negativa.",
    "time_exceeds_duration": "Marca de tiempo {time} > duración vídeo {duration}.",
    "invalid_trim_points": "Marcas de tiempo para corte inválidas.",
    "missing_options": "Se requiere al menos una opción.",
    "insufficient_inputs": (
        "Se requieren al menos proporcionar dos vídeos para este comando."
    ),
}

Warnings = {
    "scale_rejected_equal": "Escalado rechazado: {scale} = altura original {height}.",
    "scale_rejected_increase": (
        "Escalado a {scale}p no aplicado: resolución mayor que la original ({height}p)."
    ),
    "missing_options": "Se requiere al menos una opción.",
}

Info = {
    "config_saved": "Guardando config.toml",
    "concat_success": "Vídeos unidos correctamente: {output}",
    "encode_success": "Transcodificación correcta: {output}",
    "gif_success": "Generado correctamente GIF: {output}",
    "split_success": "División correcta del vídeo: {output}",
}

Debug = {
    "ffprobe_data": "Datos ffprobe: {data}",
    "ffmpeg_command": "Comando ffmpeg: {cmd}",
    "pipeline_crop": "Crop calculado: {crop}",
    "pipeline_scale": "Scale calculado: {scale}",
    "pipeline_gyrate": "Gyrate aplicado: {gyrate}",
    "pipeline_trim": "Trim points: {trim}",
    "pipeline_time": "Tiempo procesado: {time}",
}
