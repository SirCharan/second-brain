<#
.SYNOPSIS
  second-brain installer for native Windows PowerShell.

.DESCRIPTION
  The Windows-native equivalent of install.sh: copies hooks, the skill and the workflow
  into the Claude config dir, seeds the vault, registers the hooks, and offers guided setup.
  Hook registration and the install manifest come from scripts/register-hooks.py, the same
  file install.sh calls, so the two installers cannot drift apart.

  Works two ways:
    irm https://raw.githubusercontent.com/SirCharan/second-brain/main/install.ps1 | iex
    git clone https://github.com/SirCharan/second-brain; .\second-brain\install.ps1

  Re-runnable: re-running upgrades files and replaces our own hook registrations.
  Undo with uninstall.ps1.

.PARAMETER Pack
  Answer the starter-pack question up front: none, core, "core,writing", or all.

.PARAMETER NoSetup
  Skip the guided setup wizard.

.PARAMETER DryRun
  Report what would happen and write nothing.
#>
[CmdletBinding()]
param(
    [string]$Pack = "",
    [switch]$NoSetup,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$RepoUrl = "https://github.com/SirCharan/second-brain"
$Tarball = "$RepoUrl/archive/refs/heads/main.zip"
$Claude = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { Join-Path $HOME ".claude" }
$Vault = if ($env:CLAUDE_MEMORY_DIR) { $env:CLAUDE_MEMORY_DIR } else { Join-Path $HOME ".claude\second-brain-vault" }
if ($Pack -eq "none") { $Pack = "" }

# --- locate the source tree -------------------------------------------------
# Piped through iex there is no script file on disk, so self-download instead.
$Repo = if ($PSScriptRoot) { $PSScriptRoot } else { "" }
if (-not $Repo -or -not (Test-Path (Join-Path $Repo "hooks\_hooklib.py"))) {
    if ($env:SB_BOOTSTRAPPED -eq "1") {
        Write-Error "second-brain: bootstrap failed - source tree still incomplete."
        exit 1
    }
    $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("sb-" + [guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Path $tmp -Force | Out-Null
    Write-Host "second-brain -> fetching source..."
    $zip = Join-Path $tmp "main.zip"
    Invoke-WebRequest -Uri $Tarball -OutFile $zip -UseBasicParsing
    Expand-Archive -Path $zip -DestinationPath $tmp -Force
    $src = Get-ChildItem -Path $tmp -Directory | Where-Object { $_.Name -like "second-brain-*" } | Select-Object -First 1
    if (-not $src -or -not (Test-Path (Join-Path $src.FullName "hooks\_hooklib.py"))) {
        Write-Error "second-brain: downloaded archive looks wrong."
        exit 1
    }
    $env:SB_BOOTSTRAPPED = "1"
    & (Join-Path $src.FullName "install.ps1") @PSBoundParameters
    exit $LASTEXITCODE
}

$Version = (Get-Content (Join-Path $Repo "VERSION") -ErrorAction SilentlyContinue) -join ""
if (-not $Version) { $Version = "unknown" }

# --- preflight: fail BEFORE touching anything -------------------------------
# `python3` on Windows is usually the Microsoft Store stub, so probe the launcher first.
$Py = $null
foreach ($cand in @(@("py", "-3"), @("python"), @("python3"))) {
    $exe = $cand[0]
    if (-not (Get-Command $exe -ErrorAction SilentlyContinue)) { continue }
    $args = @($cand[1..($cand.Length - 1)]) + @("-c", "import sys; sys.exit(0 if sys.version_info >= (3,8) else 1)")
    & $exe @args 2>$null
    if ($LASTEXITCODE -eq 0) { $Py = $cand; break }
}
if (-not $Py) {
    Write-Host "second-brain: needs Python 3.8+ on PATH, and found none." -ForegroundColor Red
    Write-Host "  winget install Python.Python.3.12    (or install from python.org)"
    Write-Host "Nothing was installed."
    exit 1
}
# The absolute interpreter path is what goes into the hook registrations.
$PyExe = (& $Py[0] @($Py[1..($Py.Length - 1)] + @("-c", "import sys; print(sys.executable)"))).Trim()

$parent = Split-Path -Parent $Claude
if (-not (Test-Path $parent)) {
    Write-Error "second-brain: $parent does not exist. Nothing was installed."
    exit 1
}

$Settings = Join-Path $Claude "settings.json"
if (Test-Path $Settings) {
    & $PyExe -c "import json,sys; json.load(open(sys.argv[1]))" $Settings 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "second-brain: $Settings is not valid JSON, so hooks cannot be merged into it." -ForegroundColor Red
        Write-Host "Fix or move that file, then re-run. Nothing was installed."
        exit 1
    }
}

if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
    Write-Host "  ! Claude Code CLI not found on PATH - install it for the hooks to do anything."
}

Write-Host "second-brain $Version -> installing into $Claude"
if ($DryRun) {
    Write-Host "  (dry run) would copy hooks\, skills\second-brain\, workflows\vault-enrich.js"
    Write-Host "  (dry run) would seed vault at $Vault and register 9 hooks in $Settings"
    if ($Pack) {
        Write-Host "  (dry run) would offer the starter pack: $Pack"
    } else {
        Write-Host "  (dry run) would ask whether to install the starter pack (skills + vault notes)"
    }
    exit 0
}

foreach ($d in @("hooks", "skills", "workflows")) {
    New-Item -ItemType Directory -Path (Join-Path $Claude $d) -Force | Out-Null
}

# --- machinery --------------------------------------------------------------
# Ship runtime hooks only; the test suite belongs to the repo, not the user's dir.
Get-ChildItem -Path (Join-Path $Repo "hooks") -File |
    Where-Object { ($_.Extension -in ".py", ".sh") -and ($_.Name -notlike "test_*") } |
    ForEach-Object { Copy-Item $_.FullName -Destination (Join-Path $Claude "hooks") -Force }
$skillDst = Join-Path $Claude "skills\second-brain"
if (Test-Path $skillDst) { Remove-Item $skillDst -Recurse -Force }
Copy-Item (Join-Path $Repo "skills\second-brain") -Destination $skillDst -Recurse -Force
Copy-Item (Join-Path $Repo "workflows\vault-enrich.js") -Destination (Join-Path $Claude "workflows") -Force
# The starter-pack source ships with the skill, not just in the repo: piped through iex
# the repo is a temp dir, so without this the user could never add a tier later.
if (Test-Path (Join-Path $Repo "starter-pack")) {
    Copy-Item (Join-Path $Repo "starter-pack") -Destination (Join-Path $skillDst "starter-pack") -Recurse -Force
}
Write-Host "  + hooks, skill, workflow copied"

# --- vault ------------------------------------------------------------------
if (-not (Test-Path $Vault)) {
    Copy-Item (Join-Path $Repo "vault-template") -Destination $Vault -Recurse -Force
    New-Item -ItemType Directory -Path (Join-Path $Vault ".recall-state") -Force | Out-Null
    Write-Host "  + vault created at $Vault"
} else {
    Write-Host "  . vault already exists at $Vault (left as-is)"
    New-Item -ItemType Directory -Path (Join-Path $Vault ".recall-state") -Force | Out-Null
}

# --- register hooks + write the install manifest (idempotent) ---------------
& $PyExe (Join-Path $skillDst "scripts\register-hooks.py") $Settings $Vault $Version --python $PyExe

# Persist a non-default vault path for future sessions.
if ($Vault -ne (Join-Path $HOME ".claude\second-brain-vault")) {
    if (-not [Environment]::GetEnvironmentVariable("CLAUDE_MEMORY_DIR", "User")) {
        [Environment]::SetEnvironmentVariable("CLAUDE_MEMORY_DIR", $Vault, "User")
        Write-Host "  + CLAUDE_MEMORY_DIR set for your user account"
    }
}

# --- guided setup -----------------------------------------------------------
# SB_REPO points setup.py at this checkout, so a re-run from a clone picks up local
# edits rather than the copy installed above.
$env:SB_REPO = $Repo
$env:CLAUDE_MEMORY_DIR = $Vault
$setup = Join-Path $skillDst "scripts\setup.py"
$packScript = Join-Path $skillDst "scripts\starter-pack.py"
if (-not $NoSetup -and (Test-Path $setup)) {
    Write-Host ""
    if ($Pack) { & $PyExe $setup --pack $Pack } else { & $PyExe $setup }
} elseif ($Pack -and (Test-Path $packScript)) {
    Write-Host ""
    & $PyExe $packScript --tiers $Pack
}

Write-Host ""
Write-Host "second-brain $Version installed."
Write-Host "  Vault:  $Vault"
Write-Host "  Check:  $PyExe `"$(Join-Path $skillDst 'scripts\doctor.py')`""
Write-Host "  Pack:   $PyExe `"$packScript`" --list"
Write-Host "  Undo:   .\uninstall.ps1"
Write-Host ""
Write-Host "Restart Claude Code (or start a new session) so the hooks load."
