<#
#JSON-BEGIN
{
  "commands": [
    {
      "name": "CONCAT DEMUX MISMO VIDEO",
      "command": "uv run pymedia concat ./VIDs/bunny_1080p_av1_no_sound.mp4 ./VIDs/bunny_1080p_av1_no_sound.mp4 -o concat_demux_mismo_video.mp4"
    },
    {
      "name": "CONCAT DEMUX EN DISTINTOS VIDEOS COMPATIBLES",
      "command": "uv run pymedia concat ./VIDs/trees_720p_h264_sound.mp4 ./VIDs/lake_720p_h264_sound.mp4 -o concat_demux_videos_compatibles.mp4"
    },
    {
      "name": "CONCAT TRANSCODIFICADO",
      "command": "uv run pymedia concat ./VIDs/trees_720p_h264_sound.mp4 ./VIDs/lake_720p_h264_sound.mp4 -g 90 -c 0,0,100,100 -s 480 -o concat_filter_transcodificado.mp4"
    },
    {
      "name": "CONCAT INCOMPATIBLE",
      "command": "uv run pymedia concat ./VIDs/bunny_1080p_av1_no_sound.mp4 ./VIDs/jellyfish_360p_h264_no_sound.mp4 -o concat_filter_incompatibles.mp4"
    },
    {
      "name": "ENCODE SIMPLE",
      "command": "uv run pymedia encode ./VIDs/flowers_720p_h264_no_sound.mp4 -r -o encode_individual.mp4"
    },
    {
      "name": "ENCODE EN MASA",
      "command": "uv run pymedia encode ./VIDs/jellyfish_360p_h264_no_sound.mp4 ./VIDs/lake_720p_h264_sound.mp4 -r -o .encode_multiple.mp4"
    },
    {
      "name": "DIVISION SIMPLE",
      "command": "uv run pymedia split ./VIDs/lake_720p_h264_sound.mp4 -t 2,9 -o division_simple.mp4"
    },
    {
      "name": "DIVISION TRANCODIFICADA",
      "command": "uv run pymedia split ./VIDs/sintel_818p_h264_no_sound.mp4 -t 3 -s 720 -g 180 -o division_transcodificada.mp4"
    },
    {
      "name": "GIF",
      "command": "uv run pymedia gif ./VIDs/jellyfish_360p_h264_no_sound.mp4 -o gif_simple.gif"
    },
    {
      "name": "GIF TRANSCODIFICADO",
      "command": "uv run pymedia gif ./VIDs/world_1080p_h264_sound.mp4 -sp 5 -ep 10 -s 240 -c 200,200,0,0 -o gif_transcodificado.gif"
    },
    {
      "name": "ARCHIVOS GENERADOS",
      "command": "ls *.mp4; ls *.gif"
    },
    {
      "name": "BORRADO",
      "command": "rm *.mp4; rm *.gif"
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
    Write-Host "Ejecutando: $($item.name)" -ForegroundColor yellow
    Invoke-Expression $item.command
}
