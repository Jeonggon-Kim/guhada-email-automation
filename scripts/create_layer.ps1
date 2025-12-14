# Layer Creation Script (PowerShell)

Write-Host "📦 Creating Lambda Layer..." -ForegroundColor Cyan

# Clean up
if (Test-Path "layer_package") { Remove-Item -Recurse -Force "layer_package" }
if (Test-Path "layer.zip") { Remove-Item -Force "layer.zip" }

New-Item -ItemType Directory -Force -Path "layer_package/python" | Out-Null

# Install dependencies for Linux
# Excluding boto3 to save space
Get-Content requirements.txt | Where-Object { $_ -notmatch "boto3" } | Set-Content requirements_layer.txt

Write-Host "Downloading libraries..." -ForegroundColor Cyan
pip install -r requirements_layer.txt -t layer_package/python --platform manylinux2014_x86_64 --implementation cp --python-version 3.12 --only-binary=:all: --upgrade

Remove-Item requirements_layer.txt

# Cleanup unnecessary files
Write-Host "Cleaning up..." -ForegroundColor Cyan
Remove-Item -Recurse -Force "layer_package/python/boto3" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "layer_package/python/botocore" -ErrorAction SilentlyContinue
Get-ChildItem "layer_package/python" -Include "__pycache__", "tests", "test", "docs", "examples" -Recurse | Remove-Item -Recurse -Force
Get-ChildItem "layer_package/python" -Include "*.pyc", "*.pyo" -Recurse | Remove-Item -Force

# Zip
Write-Host "Zipping..." -ForegroundColor Cyan
Compress-Archive -Path "layer_package/*" -DestinationPath "layer.zip" -Force

# Cleanup
Remove-Item -Recurse -Force "layer_package"

Write-Host "✓ layer.zip created!" -ForegroundColor Green
Write-Host "Upload this file to AWS Lambda -> Layers"
