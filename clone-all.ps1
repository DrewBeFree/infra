# Clone all repositories to their target directories
param([string]$BaseDirectory = $null, [switch]$DryRun = $false)

$manifestPath = Join-Path $PSScriptRoot "repos.json"
if (-not (Test-Path $manifestPath)) { Write-Error "repos.json not found"; exit 1 }

$manifest = Get-Content $manifestPath | ConvertFrom-Json
if (-not $BaseDirectory) { $BaseDirectory = $manifest.baseDirectory }

Write-Host "Cloning repositories to: $BaseDirectory" -ForegroundColor Cyan
if ($DryRun) { Write-Host "[DRY RUN MODE]`n" -ForegroundColor Yellow }

$successCount = 0
$skipCount = 0
$failCount = 0

foreach ($repo in $manifest.repositories) {
    $targetPath = Join-Path $BaseDirectory $repo.targetDirectory
    $repoName = $repo.name
    $gitUrl = $repo.github

    if (Test-Path $targetPath) {
        Write-Host "⊘ $repoName - Already exists" -ForegroundColor Gray
        $skipCount++
        continue
    }

    $parentDir = Split-Path $targetPath -Parent
    if (-not (Test-Path $parentDir)) {
        if ($DryRun) {
            Write-Host "  [DRY RUN] Would create: $parentDir" -ForegroundColor Yellow
        } else {
            New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
        }
    }

    Write-Host "→ $repoName" -ForegroundColor Cyan

    if ($DryRun) {
        Write-Host "  Would clone to: $targetPath" -ForegroundColor Yellow
        $successCount++
    } else {
        Push-Location $parentDir
        git clone $gitUrl (Split-Path $targetPath -Leaf) 2>$null
        $success = $?
        Pop-Location

        if ($success) {
            Write-Host "  ✓ Success" -ForegroundColor Green
            $successCount++
        } else {
            Write-Host "  ✗ Failed" -ForegroundColor Red
            $failCount++
        }
    }
}

Write-Host "`n────────────────────────" -ForegroundColor Gray
Write-Host "✓ Cloned: $successCount" -ForegroundColor Green
Write-Host "⊘ Skipped: $skipCount" -ForegroundColor Gray
Write-Host "✗ Failed: $failCount" -ForegroundColor Red

if ($failCount -gt 0) { exit 1 }
