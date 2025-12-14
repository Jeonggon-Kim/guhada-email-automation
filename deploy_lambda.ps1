# Lambda Deployment Script (PowerShell) - Cross Platform Fix

Write-Host "Package creation started..." -ForegroundColor Cyan

# Clean up temp directories
if (Test-Path "lambda_package") {
    Remove-Item -Recurse -Force "lambda_package"
}
if (Test-Path "lambda_function.zip") {
    Remove-Item -Force "lambda_function.zip"
}

New-Item -ItemType Directory -Force -Path "lambda_package" | Out-Null

# Install dependencies (excluding boto3)
Get-Content requirements.txt | Where-Object { $_ -notmatch "boto3" } | Set-Content requirements_lambda.txt

# FORCE LINUX BINARIES (This fixes the grpc/cygrpc error)
Write-Host "Downloading Linux binaries..." -ForegroundColor Cyan
pip install -r requirements_lambda.txt -t lambda_package/ --platform manylinux2014_x86_64 --implementation cp --python-version 3.12 --only-binary=:all: --upgrade

Remove-Item requirements_lambda.txt

# Copy source code
Copy-Item "lambda_function.py" -Destination "lambda_package/"
Copy-Item "auth_provider_aws.py" -Destination "lambda_package/"
Copy-Item "graph_client.py" -Destination "lambda_package/"
Copy-Item "email_processor.py" -Destination "lambda_package/"
Copy-Item "llm_service.py" -Destination "lambda_package/"
Copy-Item "config.py" -Destination "lambda_package/"

# Create ZIP
Write-Host "Zipping files..." -ForegroundColor Cyan
Compress-Archive -Path "lambda_package/*" -DestinationPath "lambda_function.zip" -Force

# Cleanup
Remove-Item -Recurse -Force "lambda_package"

Write-Host "✓ lambda_function.zip created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Please upload this new zip file to AWS Lambda."
