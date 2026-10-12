# Windows PowerShell version of make-archive.sh
#   powershell -ExecutionPolicy Bypass -File scripts\make-archive.ps1
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

$date = Get-Date -Format "yyyy-MM-dd"
$out = "archive\$date"
New-Item -ItemType Directory -Force -Path $out | Out-Null

Write-Host "==> Building image"
docker build -t "moodqueue:$date" -t moodqueue:latest .

Write-Host "==> Saving image (this is the important file)"
docker save -o "$out\moodqueue-image.tar" "moodqueue:$date"

Write-Host "==> Saving source code"
git archive --format=zip -o "$out\moodqueue-source.zip" HEAD

$commit = git rev-parse --short HEAD
@"
MoodQueue backup - $date - commit $commit

1. Install Docker (or Podman).
2. docker load -i moodqueue-image.tar
3. docker run -p 8000:8000 -v moodqueue-data:/app/data moodqueue:$date
4. Open http://localhost:8000

No account or API key is needed.
"@ | Set-Content "$out\RESTORE.txt"

Write-Host "==> Done: $out"
Get-ChildItem $out
Write-Host "Copy this folder somewhere safe (external drive + cloud)."
