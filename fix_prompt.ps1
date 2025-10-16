# PowerShell Prompt Fix Script
# Fixes the "(Dedup)" ghost prompt issue

Write-Host "=== Fixing PowerShell Prompt ===" -ForegroundColor Cyan
Write-Host ""

# Define the new prompt function
function global:prompt {
    # Conda environment indicator
    if ($env:CONDA_DEFAULT_ENV) {
        Write-Host "($env:CONDA_DEFAULT_ENV) " -NoNewline -ForegroundColor Yellow
    }
    
    # UV/venv virtual environment indicator
    if ($env:VIRTUAL_ENV) {
        $venvName = Split-Path $env:VIRTUAL_ENV -Leaf
        Write-Host "($venvName) " -NoNewline -ForegroundColor Cyan
    }
    
    # Path and prompt
    Write-Host "PS " -NoNewline
    Write-Host "$($executionContext.SessionState.Path.CurrentLocation)" -NoNewline -ForegroundColor Green
    return "> "
}

Write-Host "Prompt function updated!" -ForegroundColor Green
Write-Host ""
Write-Host "Current environment:" -ForegroundColor Yellow
Write-Host "  Conda: $env:CONDA_DEFAULT_ENV"
Write-Host "  Virtual Env: $env:VIRTUAL_ENV"
Write-Host "  Python: $((Get-Command python -ErrorAction SilentlyContinue).Source)"
Write-Host ""
Write-Host "To make this permanent, add the prompt function to your PowerShell profile:" -ForegroundColor Cyan
Write-Host "  1. Run: notepad `$PROFILE" -ForegroundColor White
Write-Host "  2. Copy the prompt function from this script" -ForegroundColor White
Write-Host "  3. Save and reload: . `$PROFILE" -ForegroundColor White
Write-Host ""

