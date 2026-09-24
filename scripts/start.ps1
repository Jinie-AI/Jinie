$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot
if (!(Test-Path ".venv")) { py -3.12 -m venv .venv }
& .\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
if ($LASTEXITCODE -ne 0) { throw "Backend installation failed." }
Push-Location frontend
npm ci
if ($LASTEXITCODE -ne 0) { throw "Frontend installation failed." }
Pop-Location
Start-Process powershell -WorkingDirectory "$projectRoot\backend" -ArgumentList '-NoExit', '-Command', "& '$projectRoot\.venv\Scripts\python.exe' -m uvicorn main:app --host 127.0.0.1 --port 8000"
Start-Process powershell -WorkingDirectory "$projectRoot\frontend" -ArgumentList '-NoExit', '-Command', 'npm run dev -- --host 127.0.0.1'
Write-Host 'Open http://127.0.0.1:5173 after both servers start.'
