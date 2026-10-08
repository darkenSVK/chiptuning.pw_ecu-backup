# Publikuje zmeny: GitHub (git) + Google Drive (rclone).
# Spustenie z priecinka repa:  .\publish.ps1 "popis zmeny"
# Najprv len nasucho (nic nezmeni na Disku):  .\publish.ps1 -DryRun

param(
    [string]$Message = "Update ECU files",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot          # vzdy priecinok repa, nie aktualny adresar

$Remote = "gdrive:.chiptuning.pw_ecu-backup"
$Exclude = @("--exclude", ".git/**", "--exclude", ".github/**",
             "--exclude", "New_files/**", "--exclude", "incoming/**",
             "--exclude", "publish.ps1")

Write-Host "`n== GitHub ==" -ForegroundColor Cyan
git pull
if (-not $DryRun) {
    git add -A
    git diff --cached --quiet
    if ($LASTEXITCODE -ne 0) {
        git commit -m $Message
        git push
    } else {
        Write-Host "Ziadne zmeny na commit."
    }
}

Write-Host "`n== Google Drive ==" -ForegroundColor Cyan
if ($DryRun) {
    rclone sync . $Remote @Exclude --dry-run
} else {
    rclone sync . $Remote @Exclude -P
}

Write-Host "`nHotovo." -ForegroundColor Green
