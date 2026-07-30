<#
.SYNOPSIS
  Remove second-brain from a native Windows install.

.DESCRIPTION
  The Windows-native equivalent of uninstall.sh. It reads the install manifest written at
  install time and removes exactly what was installed: our hook files, the skill directory,
  the workflow, any starter-pack skills, and our hook registrations. Notes are never touched
  unless you pass -PurgeVault.

.PARAMETER PurgeVault
  Also delete the vault and every note in it. Asks first.

.PARAMETER DryRun
  Report what would happen and remove nothing.
#>
[CmdletBinding()]
param(
    [switch]$PurgeVault,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$Claude = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { Join-Path $HOME ".claude" }
$Vault = if ($env:CLAUDE_MEMORY_DIR) { $env:CLAUDE_MEMORY_DIR } else { Join-Path $HOME ".claude\second-brain-vault" }
$Manifest = Join-Path $Vault "_infra\_install-manifest.json"

$Py = $null
foreach ($cand in @(@("py", "-3"), @("python"), @("python3"))) {
    if (-not (Get-Command $cand[0] -ErrorAction SilentlyContinue)) { continue }
    $probe = @($cand[1..($cand.Length - 1)]) + @("-c", "import sys; sys.exit(0 if sys.version_info >= (3,8) else 1)")
    & $cand[0] @probe 2>$null
    if ($LASTEXITCODE -eq 0) { $Py = $cand; break }
}
if (-not $Py) {
    Write-Error "second-brain: needs Python 3.8+ on PATH to read the manifest."
    exit 1
}
$PyExe = (& $Py[0] @($Py[1..($Py.Length - 1)] + @("-c", "import sys; print(sys.executable)"))).Trim()

Write-Host "second-brain -> uninstalling from $Claude"
if (-not (Test-Path $Manifest)) {
    Write-Host "  ! no manifest at $Manifest - falling back to the known layout"
}

$env:DRY_RUN = if ($DryRun) { "1" } else { "0" }
# One implementation: the same removal logic uninstall.sh runs, driven from Python so
# the two scripts cannot disagree about what belongs to us.
$code = @'
import json, os, shutil, sys
claude, vault, manifest = sys.argv[1], sys.argv[2], sys.argv[3]
dry = os.environ.get("DRY_RUN") == "1"
def say(*a): print(("  (dry run)" if dry else "  +"), *a)

OURS = ("session-memory","session-resume","interview-nudge","memory-recall","context-monitor",
        "memory-lint","stuck-detector","capture-exchange","precompact-carryover")
man = {}
if os.path.exists(manifest):
    try: man = json.load(open(manifest))
    except Exception: man = {}

hooks_dir = os.path.join(claude, "hooks")
shipped = set(man.get("hook_names", OURS)) | {"_hooklib", "memory-embed", "context-dump", "sb_rank"}
removed = 0
if os.path.isdir(hooks_dir):
    for f in sorted(os.listdir(hooks_dir)):
        stem = os.path.splitext(f)[0]
        if stem in shipped and f.endswith((".py", ".sh")):
            if not dry: os.remove(os.path.join(hooks_dir, f))
            removed += 1
say(f"removed {removed} hook file(s)")
# Our own import cache, created the first time a hook ran. Ours to clean up.
pyc = os.path.join(hooks_dir, "__pycache__")
if os.path.isdir(pyc):
    if not dry: shutil.rmtree(pyc, ignore_errors=True)
    say("removed", pyc)

for d in man.get("dirs", [os.path.join(claude, "skills", "second-brain")]):
    if os.path.isdir(d):
        if not dry: shutil.rmtree(d)
        say("removed", d)
for w in man.get("workflows", [os.path.join(claude, "workflows", "vault-enrich.js")]):
    if os.path.exists(w):
        if not dry: os.remove(w)
        say("removed", w)

settings = man.get("settings") or os.path.join(claude, "settings.json")
if os.path.exists(settings):
    try:
        d = json.load(open(settings))
    except Exception:
        print("  ! settings.json is not valid JSON - left untouched")
        d = None
    if d is not None:
        H = d.get("hooks", {})
        def is_ours(e):
            return any(o in h.get("command", "") for h in e.get("hooks", []) for o in OURS)
        n = 0
        for ev in list(H):
            keep = [e for e in H[ev] if not is_ours(e)]
            n += len(H[ev]) - len(keep)
            if keep: H[ev] = keep
            else: H.pop(ev)
        if not H: d.pop("hooks", None)
        if d.get("env", {}).get("CLAUDE_MEMORY_DIR"):
            d["env"].pop("CLAUDE_MEMORY_DIR", None)
            if not d["env"]: d.pop("env")
        if not dry:
            shutil.copy2(settings, settings + ".pre-uninstall.bak")
            json.dump(d, open(settings, "w"), indent=2)
        say(f"de-registered {n} hook entr(ies) from settings.json")
        bak = man.get("settings_backup")
        if bak and os.path.exists(bak):
            print(f"  . pre-install backup still available: {bak}")
'@
$tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("sb-uninstall-" + [guid]::NewGuid().ToString("N") + ".py")
Set-Content -Path $tmp -Value $code -Encoding UTF8
try {
    & $PyExe $tmp $Claude $Vault $Manifest
} finally {
    Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}

if ($PurgeVault) {
    if ($DryRun) {
        Write-Host "  (dry run) would delete the vault at $Vault"
    } else {
        $ans = Read-Host "Delete the vault and every note at $Vault? [y/N]"
        if ($ans -match '^[Yy]') {
            Remove-Item $Vault -Recurse -Force
            Write-Host "  + vault deleted"
        } else {
            Write-Host "  . vault kept"
        }
    }
} else {
    Write-Host "  . vault kept at $Vault (use -PurgeVault to remove it)"
}

Write-Host ""
Write-Host "Done. Restart Claude Code so it stops loading the hooks."
