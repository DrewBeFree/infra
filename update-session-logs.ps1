# Update SESSION_LOG.md in all touched repositories
# Detects repos with recent git activity and updates/creates SESSION_LOG.md
# Reads baseDirectory from repos.json (portable across systems)
# Usage: .\update-session-logs.ps1 -Summary "What was done" -Stopped "Where we stopped" -Next "What's next"

param(
    [string]$Summary = "",
    [string]$Stopped = "",
    [string]$Next = "",
    [string]$BaseDirectory = $null
)

if (-not $Summary) {
    Write-Host "Usage: .\update-session-logs.ps1 -Summary `"..`" -Stopped `"..`" -Next `"..`"" -ForegroundColor Yellow
    exit 1
}

# Load base directory from repos.json
$manifestPath = Join-Path $PSScriptRoot "repos.json"
if (-not (Test-Path $manifestPath)) {
    Write-Error "repos.json not found at $manifestPath"
    exit 1
}

$manifest = Get-Content $manifestPath | ConvertFrom-Json
if (-not $BaseDirectory) {
    $BaseDirectory = $manifest.baseDirectory
}

$today = Get-Date -Format "yyyy-MM-dd"
$repos = @()

# Find all git repos with recent changes
Get-ChildItem $BaseDirectory -Directory -Force | ForEach-Object {
    $repoPath = $_.FullName
    $gitDir = Join-Path $repoPath ".git"

    if (Test-Path $gitDir) {
        Push-Location $repoPath

        # Check for uncommitted changes or recent commits (last hour)
        $hasChanges = git status --porcelain
        $recentCommit = git log --oneline -1 --since="1 hour ago"

        Pop-Location

        if ($hasChanges -or $recentCommit) {
            $repos += @{
                Name = $_.Name
                Path = $repoPath
            }
        }
    }
}

if ($repos.Count -eq 0) {
    Write-Host "No repositories with recent changes found." -ForegroundColor Gray
    exit 0
}

Write-Host "Found $($repos.Count) repository(ies) with recent changes:`n" -ForegroundColor Cyan
$repos | ForEach-Object { Write-Host "  • $($_.Name)" -ForegroundColor Gray }
Write-Host ""

foreach ($repo in $repos) {
    $repoPath = $repo.Path
    $repoName = $repo.Name
    $logPath = Join-Path $repoPath "SESSION_LOG.md"

    Write-Host "Updating: $repoName" -ForegroundColor Cyan

    # Create session log entry
    $entry = @"
## $today

**What we did:**
$Summary

**Where we stopped:**
$Stopped

**Next up:**
$Next

"@

    # Read existing log or create new
    if (Test-Path $logPath) {
        $existing = Get-Content $logPath -Raw
        $newContent = "# Session Log`n`n$entry`n$existing"
    } else {
        $newContent = "# Session Log`n`n$entry"
    }

    # Write updated log
    $newContent | Out-File $logPath -Encoding UTF8 -Force

    # Commit and push
    Push-Location $repoPath
    git add SESSION_LOG.md
    git commit -m "Update session log: $($today)" -ErrorAction SilentlyContinue | Out-Null
    git push 2>&1 | Out-Null
    Pop-Location

    Write-Host "  ✓ Updated" -ForegroundColor Green
}

Write-Host "`n✓ Session logs updated across all touched repositories" -ForegroundColor Green
