# Run one of the design system's scripts with the right Python, on Windows.
#
#     powershell -NoProfile -ExecutionPolicy Bypass -File run.ps1 doctor.py
#
# Uses the private Python that setup.ps1 installs, never a bare `python` (on many machines
# that is only a Microsoft Store shortcut). Exits 3 with a plain-language message when setup
# has not been run.
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$HomeDir = if ($env:WWT_DESIGN_HOME) { $env:WWT_DESIGN_HOME } else { Join-Path $env:USERPROFILE ".wwtdigital-deck-design" }
$Py = Join-Path $HomeDir "venv\Scripts\python.exe"
$env:PLAYWRIGHT_BROWSERS_PATH = Join-Path $HomeDir "browsers"

if ($args.Count -lt 1) { Write-Host "usage: run.ps1 <script.py> [arguments]"; exit 2 }
if (-not (Test-Path $Py)) {
  Write-Host @"
SETUP NEEDED: the WWTDigital design system has not been set up on this machine yet.
It is a one-time step, a few minutes, no admin rights. It downloads a private copy of
Python and its packages (about 330 MB of disk space) into $HomeDir. To run it:
    powershell -NoProfile -ExecutionPolicy Bypass -File "$Here\setup.ps1"
"@
  exit 3
}
$Script = Join-Path $Here ("..\skills\wwtdigital-deck-design\scripts\" + $args[0])
$Rest = if ($args.Count -gt 1) { $args[1..($args.Count - 1)] } else { @() }
& $Py $Script @Rest
exit $LASTEXITCODE
