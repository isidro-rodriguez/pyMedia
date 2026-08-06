<#
#JSON-BEGIN
{
  "commands": [
    {
      "name": "Concat simple",
      "command": "uv run pymedia concat ./VIDs/bunny_1080p_av1_no_sound.mp4 ./VIDs/sintel_1080_h264_no_sound.mp4 -o ./VIDs_output/concat_simple.mp4"
    },
    {
      "name": "Concat con transcodificación",
      "command": "uv run pymedia concat ./VIDs/trees_720p_h264_sound.mp4 ./VIDs/lake_720p_h264_sound.mp4 -g 90 -c 0,0,100,100 -o ./VIDs_output/concat_transcodificado.mp4"
    },
    {
      "name": "Concat incompatible",
      "command": "uv run pymedia concat ./VIDs/bunny_1080p_av1_no_sound.mp4 ./VIDs/jellyfish_360p_h264_no_sound.mp4 -o ./VIDs_output/concat_incompatible.mp4"
    },
    {
      "name": "Transcodificación de un vídeo",
      "command": "uv run pymedia encode ./VIDs/flowers_720p_h264_no_sound.mp4 -r -o ./VIDs_output/encode_individual.mp4"
    },
    {
      "name": "Transodificación en masa",
      "command": "uv run pymedia encode ./VIDs/jellyfish_360p_h264_no_sound.mp4 ./VIDs/lake_720p_h264_sound.mp4 -r -o ./VIDs_output/encode_multiple.mp4"
    },
    {
      "name": "División simple",
      "command": "uv run pymedia split ./VIDs/lake_720p_h264_sound.mp4 -t 2,9 -o ./VIDs_output/division_simple.mp4"
    },
    {
      "name": "División transcodificada",
      "command": "uv run pymedia split ./VIDs/sintel_1080_h264_no_sound.mp4 -t 3 -s 720 -g 180 -o ./VIDs_output/division_transcodificada.mp4"
    },
    {
      "name": "Generación de Gif",
      "command": "uv run pymedia gif ./VIDs/trees_720p_h264_sound.mp4 -sp 5 -ep 10 -o ./VIDs_output/gif_simple.mp4"
    },
    {
      "name": "Generación de Gif transcodificado",
      "command": "uv run pymedia gif ./VIDs/world_1080p_h264_sound.mp4 -sp 5 -ep 10 -s 240 -c 200,200,0,0 -o ./VIDs_output/gif_transcodificado.mp4"
    }
  ]
}
#JSON-END
#>

$content = Get-Content $PSCommandPath -Raw

$json = ($content -split '#JSON-BEGIN',2)[1]
$json = ($json -split '#JSON-END',2)[0]

$header = $json | ConvertFrom-Json

# Ejecutar los comandos
foreach ($item in $header.commands) {
    Write-Host "Ejecutando: $($item.name)"
    Invoke-Expression $item.command
}

