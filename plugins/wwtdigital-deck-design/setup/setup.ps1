# One-time setup for the WWTDigital design system on Windows.
#
#     powershell -NoProfile -ExecutionPolicy Bypass -File setup.ps1
#
# Written for people who have never installed Python and should not have to. It needs no
# admin rights, changes nothing system-wide and touches nothing outside
# %USERPROFILE%\.wwtdigital-deck-design:
#
#   1. uv, a small self-contained tool that manages Python (astral.sh/uv). Used from PATH if
#      it is already installed, otherwise a pinned release is downloaded from GitHub into
#      .wwtdigital-deck-design\uv after its SHA-256 is checked.
#   2. A private Python and the packages in requirements.txt, in .wwtdigital-deck-design\venv.
#      uv fetches its own Python, so a missing Python or the Microsoft Store shortcut does
#      not matter.
#   3. A browser for rendering. Microsoft Edge (on every Windows machine) or Google Chrome is
#      used if present; otherwise Playwright's Chromium (~150 MB) is downloaded.
#
# Safe to run again: finished steps are skipped. Delete .wwtdigital-deck-design\venv to redo it.
$ErrorActionPreference = "Stop"

$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$HomeDir = if ($env:WWT_DESIGN_HOME) { $env:WWT_DESIGN_HOME } else { Join-Path $env:USERPROFILE ".wwtdigital-deck-design" }
$Venv = Join-Path $HomeDir "venv"
$Py = Join-Path $Venv "Scripts\python.exe"
$env:PLAYWRIGHT_BROWSERS_PATH = Join-Path $HomeDir "browsers"
# Keep uv's Python and download cache inside HomeDir too, instead of AppData.
$env:UV_PYTHON_INSTALL_DIR = Join-Path $HomeDir "python"
$env:UV_CACHE_DIR = Join-Path $HomeDir "cache"

function Say($m) { Write-Host "`n==> $m" }
function Fail($m) { Write-Host "`nSetup stopped: $m" -ForegroundColor Red; exit 1 }

New-Item -ItemType Directory -Force -Path $HomeDir | Out-Null

Say "Step 1 of 3: uv (the Python manager)"
$uvCmd = Get-Command uv -ErrorAction SilentlyContinue
$localUv = Join-Path $HomeDir "uv\uv.exe"
if ($uvCmd) { $Uv = $uvCmd.Source }
elseif (Test-Path $localUv) { $Uv = $localUv }
else {
  # uv comes straight from its GitHub release: one pinned version, and the download must match
  # the SHA-256 below before anything is unpacked. Nothing downloaded is ever run as a script.
  # To move to a newer uv, change the version and both hashes together, here and in setup.sh.
  $UvVersion = "0.12.17"
  $Arch = if ($env:PROCESSOR_ARCHITEW6432) { $env:PROCESSOR_ARCHITEW6432 } else { $env:PROCESSOR_ARCHITECTURE }
  switch ($Arch) {
    "AMD64" { $UvTarget = "x86_64-pc-windows-msvc";  $UvSha = "a252121d5b59398fcb137c6ea448176459a44010f33f67e0072305a637119ca7" }
    "ARM64" { $UvTarget = "aarch64-pc-windows-msvc"; $UvSha = "3e1aa6849d77f0e00dc865e4afab5c5b32de053e21fe35bf5ad5cec3734ec976" }
    default { Fail "this kind of computer ($Arch) is not supported. Install uv yourself (docs.astral.sh/uv) and run this again." }
  }
  Write-Host "Downloading uv $UvVersion into $HomeDir\uv (about 20 MB)..."
  $Tmp = Join-Path $HomeDir "uv-download"
  function FailTmp($m) { Remove-Item -Recurse -Force $Tmp -ErrorAction SilentlyContinue; Fail $m }
  if (Test-Path $Tmp) { Remove-Item -Recurse -Force $Tmp }
  New-Item -ItemType Directory -Force -Path $Tmp | Out-Null
  $Zip = Join-Path $Tmp "uv.zip"
  try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
    $ProgressPreference = "SilentlyContinue"   # the progress bar makes downloads far slower in Windows PowerShell 5
    Invoke-WebRequest -UseBasicParsing -Uri "https://github.com/astral-sh/uv/releases/download/$UvVersion/uv-$UvTarget.zip" -OutFile $Zip
  } catch { FailTmp "uv could not be downloaded. Check the network connection and try again." }
  $Got = (Get-FileHash $Zip -Algorithm SHA256).Hash
  if ($Got -ne $UvSha) { FailTmp "the uv download did not match its expected checksum, so it was discarded. Try again; if it keeps happening, tell the plugin owner." }
  try {
    Expand-Archive -Path $Zip -DestinationPath (Join-Path $Tmp "unpacked") -Force
    New-Item -ItemType Directory -Force -Path (Join-Path $HomeDir "uv") | Out-Null
    Copy-Item (Join-Path $Tmp "unpacked\uv.exe") $localUv -Force
  } catch { FailTmp "uv could not be unpacked and installed into $HomeDir\uv." }
  Remove-Item -Recurse -Force $Tmp -ErrorAction SilentlyContinue
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
  & $Uv cache clean --quiet 2>$null   # the download cache is ~230 MB and not needed again
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
& $Py (Join-Path $Here "..\skills\wwtdigital-deck-design\scripts\doctor.py")
exit 0
