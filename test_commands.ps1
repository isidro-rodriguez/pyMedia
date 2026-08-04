# pyMedia - Smoke test manual de comandos
# Uso:  powershell -ExecutionPolicy Bypass -File test_commands.ps1 [encode|split|join|gif]

param(
    [ValidateSet("encode", "split", "join", "gif")]
    [string]$Command = "encode"
)

$ErrorActionPreference = "Continue"
Set-Location $PSScriptRoot

Write-Host "=== pyMedia smoke test ($Command) ===" -ForegroundColor Green

# Limpieza de outputs previos
$videosDir = Join-Path $PSScriptRoot "VIDEOS"
if (Test-Path $videosDir) {
    Remove-Item -Path $videosDir -Recurse -Force
}
New-Item -ItemType Directory -Path $videosDir | Out-Null

function Invoke-Pymedia {
    param(
        [string]$Label,
        [string]$CmdName,
        [string[]]$CmdArgs
    )
    Write-Host "`n=== $Label ===" -ForegroundColor Cyan
    Write-Host "> uv run main $CmdName $($CmdArgs -join ' ')" -ForegroundColor DarkGray
    & uv run main $CmdName @CmdArgs
    Write-Host "Exit code: $LASTEXITCODE" -ForegroundColor Yellow
}

# ─────────── encode ───────────
if ($Command -eq "encode") {
    Invoke-Pymedia -Label "1. Remux simple" -CmdName "encode" -CmdArgs @("tests/fixtures/valid_concat/clip_01.mp4", "-r", "-o", "VIDEOS/01_remux.mp4")
    Invoke-Pymedia -Label "2. Crop 100,50,25,25" -CmdName "encode" -CmdArgs @("tests/fixtures/valid_concat/clip_01.mp4", "-c", "100,50,25,25", "-o", "VIDEOS/02_crop.mp4")
    Invoke-Pymedia -Label "3. Crop excede resolucion (omitido)" -CmdName "encode" -CmdArgs @("tests/fixtures/valid_concat/clip_01.mp4", "-c", "400,400,400,400", "-o", "VIDEOS/03_crop_omitido.mp4")
    Invoke-Pymedia -Label "4. Crop + scale 480 (1080p)" -CmdName "encode" -CmdArgs @("tests/fixtures/valid_encode/clip_06.mp4", "-c", "200,200,100,100", "-s", "480", "-o", "VIDEOS/04_crop_scale.mp4")
    Invoke-Pymedia -Label "5. Scale 480 en 720p" -CmdName "encode" -CmdArgs @("tests/fixtures/valid_encode/clip_05.mp4", "-s", "480", "-o", "VIDEOS/05_scale.mp4")
    Invoke-Pymedia -Label "6. Scale 720 en 360p (ignorado)" -CmdName "encode" -CmdArgs @("tests/fixtures/valid_concat/clip_01.mp4", "-s", "720", "-o", "VIDEOS/06_scale_ignorado.mp4")
    Invoke-Pymedia -Label "7. Gyrate 90 (1080p)" -CmdName "encode" -CmdArgs @("tests/fixtures/valid_encode/clip_06.mp4", "-g", "90", "-o", "VIDEOS/07_gyrate90.mp4")
    Invoke-Pymedia -Label "8. Gyrate 180 (480p)" -CmdName "encode" -CmdArgs @("tests/fixtures/valid_encode/clip_07.mp4", "-g", "180", "-o", "VIDEOS/08_gyrate180.mp4")
    Invoke-Pymedia -Label "9. Gyrate 270 (360p)" -CmdName "encode" -CmdArgs @("tests/fixtures/valid_concat/clip_02.mp4", "-g", "270", "-o", "VIDEOS/09_gyrate270.mp4")
    Invoke-Pymedia -Label "10. Gyrate 90 + crop 200,100,50,50 (720p)" -CmdName "encode" -CmdArgs @("tests/fixtures/valid_encode/clip_05.mp4", "-g", "90", "-c", "200,100,50,50", "-o", "VIDEOS/10_gyrate_crop.mp4")
    Invoke-Pymedia -Label "11. Gyrate 270 + scale 480" -CmdName "encode" -CmdArgs @("tests/fixtures/valid_encode/clip_06.mp4", "-g", "270", "-s", "480", "-o", "VIDEOS/11_gyrate_scale.mp4")
    Invoke-Pymedia -Label "12. Todo: crop + scale + gyrate + remux (1080p)" -CmdName "encode" -CmdArgs @("tests/fixtures/valid_encode/clip_06.mp4", "-c", "200,200,100,100", "-s", "720", "-g", "90", "-r", "-o", "VIDEOS/12_todo.mp4")
    Invoke-Pymedia -Label "13. Archivo invalido + remux (reporte)" -CmdName "encode" -CmdArgs @("tests/fixtures/invalid/empty.mp4", "-r", "-o", "VIDEOS/13_invalido.mp4")
    Invoke-Pymedia -Label "14. Multiples archivos (valido + invalido + valido)" -CmdName "encode" -CmdArgs @("tests/fixtures/valid_concat/clip_01.mp4", "tests/fixtures/invalid/empty.mp4", "tests/fixtures/valid_concat/clip_02.mp4", "-r", "-o", "VIDEOS/14_multiples.mp4")
    Invoke-Pymedia -Label "15. Sin opciones (omitido)" -CmdName "encode" -CmdArgs @("tests/fixtures/valid_concat/clip_01.mp4")
}

# ─────────── split ───────────
elseif ($Command -eq "split") {
    $videos = @(
        "tests/fixtures/valid_concat/clip_01.mp4",
        "tests/fixtures/valid_concat/clip_02.mp4",
        "tests/fixtures/valid_concat/clip_03.mp4",
        "tests/fixtures/valid_encode/clip_04.mp4",
        "tests/fixtures/valid_encode/clip_05.mp4",
        "tests/fixtures/valid_encode/clip_06.mp4",
        "tests/fixtures/valid_encode/clip_07.mp4",
        "tests/fixtures/valid_encode/clip_08.mp4",
        "tests/fixtures/valid_encode/clip_09.mp4"
    )

    $trimSets = @(
        @("00:00:01"),
        @("00:00:01", "00:00:02"),
        @("00:00:00.5", "00:00:01.5"),
        @("00:00:02")
    )

    $optionSets = @(
        @(),
        @("-r"),
        @("-c", "100,50,25,25"),
        @("-s", "480"),
        @("-g", "90"),
        @("-r", "-c", "100,50,25,25"),
        @("-s", "480", "-g", "90"),
        @("-c", "200,100,50,50", "-s", "480", "-g", "90", "-r")
    )

    for ($i = 1; $i -le 10; $i++) {
        $video = $videos | Get-Random
        $trimIndex = Get-Random -Minimum 0 -Maximum $trimSets.Count
        $trim = $trimSets[$trimIndex]
        $trimStr = $trim -join ","
        $optIndex = Get-Random -Minimum 0 -Maximum $optionSets.Count
        $opts = $optionSets[$optIndex]

        # Uno de los tests usa directorio anidado
        if ($i -eq 5) {
            $outName = "VIDEOS/nested/split_05.mp4"
        } else {
            $outName = "VIDEOS/split_{0:D2}.mp4" -f $i
        }

        $args = @("-t", $trimStr, $video, "-o", $outName) + $opts
        Invoke-Pymedia -Label "Split ${i}: $(Split-Path $video -Leaf)" -CmdName "split" -CmdArgs $args
    }

    # Casos negativos
    Invoke-Pymedia -Label "Split 11: archivo inválido" -CmdName "split" -CmdArgs @("-t", "00:00:01", "tests/fixtures/invalid/empty.mp4", "-o", "VIDEOS/split_11.mp4")
    Invoke-Pymedia -Label "Split 12: trim point excede duración" -CmdName "split" -CmdArgs @("-t", "00:00:05", "tests/fixtures/valid_concat/clip_01.mp4", "-o", "VIDEOS/split_12.mp4")
}

# ─────────── join / gif ───────────
elseif ($Command -eq "join") {
    Write-Host "`nJoin no implementado aún." -ForegroundColor Yellow
}
elseif ($Command -eq "gif") {
    Write-Host "`nGif no implementado aún." -ForegroundColor Yellow
}

# ─────────── resumen ───────────
Write-Host "`n=== Resumen ===" -ForegroundColor Green
$outputs = Get-ChildItem -Path $videosDir -Recurse -File -ErrorAction SilentlyContinue
if ($outputs) {
    Write-Host "Outputs generados en VIDEOS/:" -ForegroundColor Cyan
    $outputs | ForEach-Object { Write-Host "  $($_.FullName.Replace($PSScriptRoot + '\', ''))" -ForegroundColor DarkGray }
} else {
    Write-Host "No se generaron outputs en VIDEOS/." -ForegroundColor Yellow
}
Write-Host "`nSmoke test finalizado." -ForegroundColor Green