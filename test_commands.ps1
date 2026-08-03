# pyMedia - Smoke test manual de comandos recode
# Uso:  powershell -ExecutionPolicy Bypass -File test_commands.ps1

$ErrorActionPreference = "Continue"
Set-Location $PSScriptRoot

Write-Host "=== pyMedia smoke test ===" -ForegroundColor Green

# Limpieza de outputs previos
Get-ChildItem -Path (Join-Path $PSScriptRoot "video") -Filter "*.mp4" -Recurse -ErrorAction SilentlyContinue |
    Remove-Item -Force -ErrorAction SilentlyContinue

function Invoke-Pymedia {
    param(
        [string]$Label,
        [string[]]$CmdArgs
    )
    Write-Host "`n=== $Label ===" -ForegroundColor Cyan
    Write-Host "> uv run main recode $($CmdArgs -join ' ')" -ForegroundColor DarkGray
    & uv run main recode @CmdArgs
    Write-Host "Exit code: $LASTEXITCODE" -ForegroundColor Yellow
}

# ─────────── 1-5: basicos ───────────
Invoke-Pymedia -Label "1. Remux simple" -CmdArgs @("tests/fixtures/valid_concat/clip_01.mp4", "-r", "-o", "01_remux.mp4")
Invoke-Pymedia -Label "2. Crop 100,50,25,25" -CmdArgs @("tests/fixtures/valid_concat/clip_01.mp4", "-c", "100,50,25,25", "-o", "02_crop.mp4")
Invoke-Pymedia -Label "3. Crop excede resolucion (omitido)" -CmdArgs @("tests/fixtures/valid_concat/clip_01.mp4", "-c", "400,400,400,400", "-o", "03_crop_omitido.mp4")
Invoke-Pymedia -Label "4. Crop + scale 480 (1080p)" -CmdArgs @("tests/fixtures/valid_transcode/clip_06.mp4", "-c", "200,200,100,100", "-s", "480", "-o", "04_crop_scale.mp4")
Invoke-Pymedia -Label "5. Scale 480 en 720p" -CmdArgs @("tests/fixtures/valid_transcode/clip_05.mp4", "-s", "480", "-o", "05_scale.mp4")

# ─────────── 6-10: gyrate y combinaciones ───────────
Invoke-Pymedia -Label "6. Scale 720 en 360p (ignorado)" -CmdArgs @("tests/fixtures/valid_concat/clip_01.mp4", "-s", "720", "-o", "06_scale_ignorado.mp4")
Invoke-Pymedia -Label "7. Gyrate 90 (1080p)" -CmdArgs @("tests/fixtures/valid_transcode/clip_06.mp4", "-g", "90", "-o", "07_gyrate90.mp4")
Invoke-Pymedia -Label "8. Gyrate 180 (480p)" -CmdArgs @("tests/fixtures/valid_transcode/clip_07.mp4", "-g", "180", "-o", "08_gyrate180.mp4")
Invoke-Pymedia -Label "9. Gyrate 270 (360p)" -CmdArgs @("tests/fixtures/valid_concat/clip_02.mp4", "-g", "270", "-o", "09_gyrate270.mp4")
Invoke-Pymedia -Label "10. Gyrate 90 + crop 200,100,50,50 (720p)" -CmdArgs @("tests/fixtures/valid_transcode/clip_05.mp4", "-g", "90", "-c", "200,100,50,50", "-o", "10_gyrate_crop.mp4")

# ─────────── 11-15: combinaciones y casos especiales ───────────
Invoke-Pymedia -Label "11. Gyrate 270 + scale 480" -CmdArgs @("tests/fixtures/valid_transcode/clip_06.mp4", "-g", "270", "-s", "480", "-o", "11_gyrate_scale.mp4")
Invoke-Pymedia -Label "12. Todo: crop + scale + gyrate + remux (1080p)" -CmdArgs @("tests/fixtures/valid_transcode/clip_06.mp4", "-c", "200,200,100,100", "-s", "720", "-g", "90", "-r", "-o", "12_todo.mp4")
Invoke-Pymedia -Label "13. Archivo invalido + remux (reporte)" -CmdArgs @("tests/fixtures/invalid/empty.mp4", "-r", "-o", "13_invalido.mp4")
Invoke-Pymedia -Label "14. Multiples archivos (valido + invalido + valido)" -CmdArgs @("tests/fixtures/valid_concat/clip_01.mp4", "tests/fixtures/invalid/empty.mp4", "tests/fixtures/valid_concat/clip_02.mp4", "-r", "-o", "14_multiples.mp4")
Invoke-Pymedia -Label "15. Sin opciones (omitido)" -CmdArgs @("tests/fixtures/valid_concat/clip_01.mp4")

# ─────────── resumen ───────────
Write-Host "`n=== Resumen ===" -ForegroundColor Green
$outDir = Join-Path $PSScriptRoot "video"
$outputs = Get-ChildItem -Path $outDir -Filter "*.mp4" -ErrorAction SilentlyContinue
if ($outputs) {
    Write-Host "Outputs generados en video/:" -ForegroundColor Cyan
    $outputs | ForEach-Object { Write-Host "  $($_.Name)" -ForegroundColor DarkGray }
} else {
    Write-Host "No se generaron outputs en video/." -ForegroundColor Yellow
}
Write-Host "`nSmoke test finalizado." -ForegroundColor Green