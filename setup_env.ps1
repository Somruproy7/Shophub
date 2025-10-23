<#
Simple environment setup for Windows PowerShell:
- creates a virtual environment in .venv
- activates it (prints instructions) and installs dependencies from requirements.txt
#>

Write-Host "Creating virtual environment in .venv..."
python -m venv .venv

Write-Host "Activating virtual environment and installing requirements..."
# Activate and install
. .\.venv\Scripts\Activate.ps1
pip install --upgrade pip
if (Test-Path requirements.txt) {
    pip install -r requirements.txt
} else {
    Write-Host "requirements.txt not found in workspace root"
}

Write-Host "Done. In VS Code select the interpreter: .venv\Scripts\python.exe and reload the window if needed."
