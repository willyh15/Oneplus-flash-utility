@echo off
REM Check if conda is available
where conda >nul 2>nul
if %ERRORLEVEL%==0 (
    echo "Conda detected. Setting up conda environment..."
    conda env create -f environment.yml
    conda activate oneplus-flash-utility
    echo "Conda environment setup complete."
) else (
    echo "No conda detected. Using pip to install requirements..."
    pip install -r requirements.txt
    echo "Pip installation complete."
)

echo "Setup complete! You can now run the application."
pause