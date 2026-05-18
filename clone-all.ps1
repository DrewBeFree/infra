# Clone all repositories to their target directories
# Usage: .\clone-all.ps1
# Or:    .\clone-all.ps1 -BaseDirectory "C:\custom\path"

param(
    [string]$BaseDirectory = $null,
    [switch]$DryRun = $false
)

# Load manifest
$manifestPath = Join-Path $PSScriptRoot "repos.json"
if (-not (Test-Path $manifestPath)) {
    Write-Error "repos.json not found at $manifestPath"
    exit 1
}

$manifest = Get-Content $manifestPath | ConvertFrom-Json

# Use provided base directory or fallback to manifest
if (-not $BaseDirectory) {
    $BaseDirectory = $manifest.baseDirectory
}

Write-Host "Cloning repositories to: $BaseDirectory" -ForegroundColor Cyan
Write-Host "Manifest: $manifestPath`n" -ForegroundColor Gray

if ($DryRun) {
    Write-Host "[DRY RUN MODE] No changes will be made`n" -ForegroundColor Yellow
}

$successCount = 0
$skipCount = 0
$failCount = 0

foreach ($repo in $manifest.repositories) {
    $targetPath = Join-Path $BaseDirectory $repo.targetDirectory
    $repoName = $repo.name
    $gitUrl = $repo.github

    # Check if already cloned
    if (Test-Path $targetPath) {
        Write-Host "⊘ $repoName" -ForegroundColor Gray
        Write-Host "  Already exists at $targetPath" -ForegroundColor Gray
        $skipCount++
        continue
    }

    # Create parent directory if needed
    $parentDir = Split-Path $targetPath -Parent
    if (-not (Test-Path $parentDir)) {
        if ($DryRun) {
            Write-Host "  [DRY RUN] Would create directory: $parentDir"
        } else {
            New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
        }
    }

    # Clone repository
    Write-Host "→ $repoName" -ForegroundColor Cyan
    Write-Host "  Cloning to: $targetPath" -ForegroundColor Gray

    if ($DryRun) {
        Write-Host "  [DRY RUN] Would run: git clone $gitUrl $targetPath" -ForegroundColor Yellow
        $successCount++
    } else {
        try {
            Push-Location $parentDir
            git clone $gitUrl (Split-Path $targetPath -Leaf) 2>&1 | Out-Null
            Pop-Location

            Write-Host "  ✓ Success" -ForegroundColor Green
            $successCount++
        } catch {
            Write-Host "  ✗ Failed: $_" -ForegroundColor Red
            $failCount++
        }
    }
    Write-Host ""
}

# Summary
Write-Host "────────────────────────────────" -ForegroundColor Gray
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "  ✓ Cloned: $successCount" -ForegroundColor Green
Write-Host "  ⊘ Skipped: $skipCount" -ForegroundColor Gray
Write-Host "  ✗ Failed: $failCount" -ForegroundColor Red

if ($failCount -gt 0) {
    exit 1
}
