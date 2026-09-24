# One-time setup for the WWTDigital design system on Windows.
#
#     powershell -NoProfile -ExecutionPolicy Bypass -File setup.ps1
#
# Written for people who have never installed Python and should not have to. It needs no
# admin rights, changes nothing system-wide and touches nothing outside
# %USERPROFILE%\.wwtdigital-design:
#
#   1. uv, a small self-contained tool that manages Python (astral.sh/uv). Used from PATH if
#      it is already installed, otherwise downloaded into .wwtdigital-design\uv.
#   2. A private Python and the packages in requirements.txt, in .wwtdigital-design\venv.
#      uv fetches its own Python, so a missing Python or the Microsoft Store shortcut does
#      not matter.
#   3. A browser for rendering. Microsoft Edge (on every Windows machine) or Google Chrome is
#      used if present; otherwise Playwright's Chromium (~150 MB) is downloaded.
#
# Safe to run again: finished steps are skipped. Delete .wwtdigital-design\venv to redo it.
$ErrorActionPreference = "Stop"

$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$HomeDir = if ($env:WWT_DESIGN_HOME) { $env:WWT_DESIGN_HOME } else { Join-Path $env:USERPROFILE ".wwtdigital-design" }
$Venv = Join-Path $HomeDir "venv"
$Py = Join-Path $Venv "Scripts\python.exe"
$env:PLAYWRIGHT_BROWSERS_PATH = Join-Path $HomeDir "browsers"

function Say($m) { Write-Host "`n==> $m" }
function Fail($m) { Write-Host "`nSetup stopped: $m" -ForegroundColor Red; exit 1 }

New-Item -ItemType Directory -Force -Path $HomeDir | Out-Null

Say "Step 1 of 3: uv (the Python manager)"
$uvCmd = Get-Command uv -ErrorAction SilentlyContinue
$localUv = Join-Path $HomeDir "uv\uv.exe"
if ($uvCmd) { $Uv = $uvCmd.Source }
elseif (Test-Path $localUv) { $Uv = $localUv }
else {
  Write-Host "Downloading uv into $HomeDir\uv (about 15 MB)..."
  try {
    $env:UV_INSTALL_DIR = Join-Path $HomeDir "uv"
    $env:UV_NO_MODIFY_PATH = "1"
    Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression | Out-Null
  } catch { Fail "uv could not be downloaded. Check the network connection and try again." }
  $Uv = $localUv
}
Write-Host "Using $Uv"

Say "Step 2 of 3: Python and the design system's packages"
$Req = Join-Path $Here "requirements.txt"
$Hash = (Get-FileHash $Req -Algorithm SHA256).Hash
$Marker = Join-Path $HomeDir ".requirements"
if ((Test-Path $Py) -and (Test-Path $Marker) -and ((Get-Content $Marker -Raw).Trim() -eq $Hash)) {
  Write-Host "Already installed."
} else {
  if (-not (Test-Path $Py)) {
    & $Uv venv --quiet --python 3.12 $Venv
    if ($LASTEXITCODE -ne 0) { Fail "a private Python could not be created. Check the network connection and try again." }
  }
  & $Uv pip install --quiet --python $Py -r $Req
  if ($LASTEXITCODE -ne 0) { Fail "the packages could not be installed. Check the network connection and try again." }
  Set-Content -Path $Marker -Value $Hash
  Write-Host "Installed."
}

Say "Step 3 of 3: a browser for rendering slides"
$browsers = @(
  "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
  "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
  "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
  "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
  "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
)
if ($browsers | Where-Object { $_ -and (Test-Path $_) }) {
  Write-Host "Using the Edge or Chrome already on this machine."
} else {
  Write-Host "No Edge or Chrome found. Downloading Chromium (about 150 MB)..."
  & $Py -m playwright install chromium
  if ($LASTEXITCODE -ne 0) { Fail "the browser could not be downloaded. Installing Google Chrome also fixes this." }
}

Say "Checking the result"
& $Py (Join-Path $Here "..\skills\wwtdigital-design-system\scripts\doctor.py")
exit 0
