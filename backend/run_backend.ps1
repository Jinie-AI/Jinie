$ErrorActionPreference = 'Stop'
$backendDirectory = $PSScriptRoot
$projectDirectory = Split-Path -Parent $backendDirectory
$pythonExecutable = Join-Path $projectDirectory '.venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $pythonExecutable)) {
    throw "Project Python environment is missing: $pythonExecutable"
}

Push-Location -LiteralPath $backendDirectory
try {
    & $pythonExecutable -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
    $backendExitCode = $LASTEXITCODE
}
finally {
    Pop-Location
}
exit $backendExitCode
