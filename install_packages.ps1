# PowerShell script to install packages avoiding Windows Long Path issues
# Run this script instead of pip install -r requirements.txt

Write-Host "Creating virtual environment in current directory..." -ForegroundColor Green
python -m venv venv

Write-Host "Activating virtual environment..." -ForegroundColor Green
.\venv\Scripts\Activate.ps1

Write-Host "Upgrading pip..." -ForegroundColor Green
python -m pip install --upgrade pip --no-cache-dir

Write-Host "Installing packages (this may take a while)..." -ForegroundColor Green
Write-Host "Installing packages one by one to avoid path issues..." -ForegroundColor Yellow

$packages = @(
    "fastapi",
    "uvicorn",
    "requests",
    "sentence-transformers",
    "faiss-cpu",
    "huggingface_hub",
    "numpy"
)

foreach ($package in $packages) {
    Write-Host "Installing $package..." -ForegroundColor Cyan
    pip install $package --no-cache-dir
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error installing $package" -ForegroundColor Red
    }
}

Write-Host "`nInstallation complete! To activate the virtual environment in the future, run:" -ForegroundColor Green
Write-Host ".\venv\Scripts\Activate.ps1" -ForegroundColor Yellow

