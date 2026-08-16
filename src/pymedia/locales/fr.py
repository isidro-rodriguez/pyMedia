Cli = {
    "concat_help": "Concatène les vidéos dans lordre spécifié.",
    "crop_help": "Rogne le nombre de pixels spécifié.",
    "debug_help": "Niveau de journalisation DEBUG.",
    "encode_help": "Transcode en utilisant les options sélectionnées (nécessite au moins une option).",
    "end_point_help": "Point temporel où se termine la génération du GIF.",
    "fps_help": "Images par seconde du GIF animé.",
    "gif_help": "Génère un GIF animé à partir de la vidéo spécifiée.",
    "gyrate_help": "Fait pivoter le média de langle spécifié en degrés.",
    "invalid_path": "Pas un fichier : {path}",
    "output_help": "Nom du fichier de sortie.",
    "output_on_conflict_help": "Action à entreprendre si un fichier du même nom existe déjà.",
    "path_argument_help": "Vidéo à traiter.",
    "paths_argument_help": "Liste de vidéos à traiter.",
    "remux_help": "Réencode en utilisant le profil spécifié dans la configuration.",
    "scale_gif_help": "Redimensionne le média proportionnellement à la hauteur spécifiée.",
    "scale_video_help": "Redimensionne le média proportionnellement à la hauteur spécifiée.",
    "show_help": "Affiche ce message et quitte.",
    "split_help": "Découpe une vidéo aux points spécifiés.",
    "start_point_help": "Point temporel où commence la génération du GIF.",
    "trim_points_help": "Points de découpe pour la vidéo.",
}


ConfigValidation = {
    "invalid_audio_bit_rate": "\nParamètre de configuration non valide : encode.audio_bit_rate doit être lun des suivants : {expected}",
    "invalid_audio_codec": "\nParamètre de configuration non valide : encode.audio_codec doit être lun des suivants : {expected}",
    "invalid_channels": "\nParamètre de configuration non valide : conflictive_join.channels doit être lun des suivants : {expected}",
    "invalid_default_container": "\nParamètre de configuration non valide : encode.default_container doit être lun des suivants : {expected}",
    "invalid_fps": "\nParamètre de configuration non valide : conflictive_join.fps doit être lun des suivants : {expected}",
    "invalid_language": "\nParamètre de configuration non valide : app.language doit être lun des suivants : {expected}",
    "invalid_resize_to": "\nParamètre de configuration non valide : conflictive_join.resize_to doit être lun des suivants : {expected}",
    "invalid_video_codec": "\nParamètre de configuration non valide : encode.video_codec doit être lun des suivants : {expected}",
    "invalid_video_crf": "\nParamètre de configuration non valide : encode.video_crf doit être compris entre {min} et {max}",
    "invalid_video_preset": "\nParamètre de configuration non valide : encode.video_preset doit être lun des suivants : {expected}",
}


Debug = {
    "ffmpeg_command": "Commande FFmpeg : {cmd}",
    "ffprobe_data": "Données ffprobe : {data}",
    "pipeline_crop": "Rognage calculé : {crop}",
    "pipeline_gyrate": "Rotation appliquée : {gyrate}",
    "pipeline_scale": "Échelle calculée : {scale}",
    "pipeline_time": "Temps traité : {time}",
    "pipeline_trim": "Points de découpe : {trim}",
}


ExecutionError = {
    "cannot_create_directory": "Impossible de créer le dossier : {path}",
    "command_execution": "La commande FFmpeg {command_name} a échoué lors de lexécution. Erreur : {error}",
    "command_generation": "La commande FFmpeg {command_name} na pas été générée.",
    "ffmpeg_timeout": "Lopération FFmpeg a dépassé le délai dattente autorisé.",
    "invalid_config": "Configuration non valide : {message}",
    "invalid_config_setting": "Paramètre de configuration non valide : {setting} doit être {expected}",
    "missing_config_section": "Section de configuration manquante : {section}",
    "missing_config_setting": "Paramètre de configuration manquant : {setting}",
    "unexpected_config_setting": "Paramètre de configuration inattendu : {setting}",
}


Info = {
    "config_saved": "Enregistrement de config.toml",
    "concat_success": "Vidéos concaténées avec succès : {output}",
    "encode_success": "Transcodage terminé avec succès : {output}",
    "gif_success": "GIF généré avec succès : {output}",
    "split_success": "Vidéo découpée avec succès : {output}",
}


PipelineError = {
    "incompatible_files": "Les fichiers vidéo sont incompatibles entre eux.",
    "missing_arguments": "Arguments manquants récupérés depuis Typer.",
    "missing_argument": "Argument manquant : {argument}",
    "missing_media": "Impossible de trouver les informations média pour {path}.",
    "missing_media_property": "Impossible de trouver la propriété média {property_name}.",
    "output_on_conflict": "Processus arrêté car le fichier de sortie existe déjà.",
}


Progress = {
    "concat": "Concaténation",
    "encode": "Transcodage",
    "gif": "Génération du GIF",
    "split": "Découpe",
}


ValidationError = {
    "crop_all_zero": "Rognage non valide : toutes les valeurs sont à 0.",
    "crop_exceeds_height": "Rognage non valide : {total} >= hauteur originale {height}.",
    "crop_exceeds_width": "Rognage non valide : {total} >= largeur originale {width}.",
    "insufficient_inputs": "Au moins deux vidéos doivent être fournies pour cette commande.",
    "invalid_crop_format": "Format de rognage non valide. Attendu : LEFT,RIGHT,TOP,BOTTOM.",
    "invalid_directory_name": '{directory} contient des caractères non valides : < > : " / \\ | ? *',
    "invalid_extension": "Extension non valide {extension}. Le codec {codec} nécessite lune des extensions suivantes : {supported}.",
    "invalid_filename": '{filename} contient des caractères non valides : < > : " / \\ | ? *',
    "invalid_gif_extension": "Extension non valide {extension}. Les images GIF nécessitent le conteneur .gif.",
    "invalid_gyrate": "Format de rotation non valide. Attendu : 90 | 180 | 270.",
    "invalid_setting": "Paramètre non valide : {parameter}",
    "invalid_time_format": "Format dhorodatage non valide. Attendu : hh:mm:ss.",
    "invalid_trim_points": "Points de découpe non valides.",
    "invalid_video_extension": "Extension vidéo non valide {extension}. Les fichiers vidéo nécessitent lune des extensions suivantes : {supported}.",
    "missing_options": "Au moins une option est requise.",
    "negative_time": "Lhorodatage ne peut pas être négatif.",
    "time_exceeds_duration": "Lhorodatage {time} dépasse la durée de la vidéo {duration}.",
}


Warnings = {
    "missing_options": "Au moins une option est requise.",
    "output_exist": "Le fichier existe déjà : {file_path}.",
    "scale_rejected_equal": "Redimensionnement rejeté : {scale} = hauteur originale {height}.",
    "scale_rejected_increase": "Redimensionnement en {scale}p non appliqué : la résolution est supérieure à loriginale ({height}p).",
}
