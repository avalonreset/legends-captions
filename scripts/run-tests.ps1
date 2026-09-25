$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = Join-Path $root "src"
Set-Location -LiteralPath $root
python -m unittest discover -s tests
python -m legends_ultimate_captions.cli doctor

