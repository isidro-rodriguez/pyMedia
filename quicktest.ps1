<#
#JSON-BEGIN
{
  "commands": [
    {
      "name": "CONCAT DEMUX MISMO VIDEO",
      "command": "uv run pymedia concat ./VIDs/cell_h264_720p.mp4 ./VIDs/cell_h264_720p.mp4 -o ./DIR/concat_demux_mismo_video.mp4"
    },
    {
      "name": "CONCAT DEMUX EN DISTINTOS VIDEOS COMPATIBLES",
      "command": "uv run pymedia concat ./VIDs/cell_h264_720p.mp4 ./VIDs/mandrel_h264_720p.mp4 -o ./DIR/concat_demux_videos_compatibles.mp4"
    },
    {
      "name": "CONCAT TRANSCODIFICADO",
      "command": "uv run pymedia concat ./VIDs/cell_h264_720p.mp4 ./VIDs/mandrel_h264_720p.mp4 -g 90 -c 0,0,100,100 -s 480 -o ./DIR/concat_filter_transcodificado.mp4"
    },
    {
      "name": "CONCAT INCOMPATIBLE",
      "command": "uv run pymedia concat ./VIDs/solid_av1_480p.mp4 ./VIDs/src_h265_1080p.mp4 -o ./DIR/concat_filter_incompatibles.mp4"
    },
    {
      "name": "ENCODE SIMPLE",
      "command": "uv run pymedia encode ./VIDs/cell_h264_480p.mp4 -r -o ./DIR/encode_individual.mp4"
    },
    {
      "name": "ENCODE EN MASA",
      "command": "uv run pymedia encode ./VIDs/solid_av1_480p.mp4 ./VIDs/src_h265_720p.mp4 -r -o ./DIR/encode_multiple.mp4"
    },
    {
      "name": "DIVISION SIMPLE",
      "command": "uv run pymedia split ./VIDs/vsrc_h265_480p.mp4 -t 2,9 -o ./DIR/division_simple.mp4"
    },
    {
      "name": "DIVISION TRANCODIFICADA",
      "command": "uv run pymedia split ./VIDs/vsrc_h265_480p.mp4 -t 3 -s 720 -g 180 -o ./DIR/division_transcodificada.mp4"
    },
    {
      "name": "GIF",
      "command": "uv run pymedia gif ./VIDs/vsrc_h265_480p.mp4 -o ./DIR/gif_simple.gif"
    },
    {
      "name": "GIF TRANSCODIFICADO",
      "command": "uv run pymedia gif ./VIDs/vsrc_h265_480p.mp4 -sp 5 -ep 10 -s 240 -c 200,200,0,0 -o ./DIR/gif_transcodificado.gif"
    },
    {
      "name": "ARCHIVOS GENERADOS",
      "command": "ls ./DIR/"
    },
    {
      "name": "BORRADO",
      "command": "rmdir ./DIR/"
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
