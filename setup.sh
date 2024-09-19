#!/bin/bash

# Check if conda is available
if command -v conda >/dev/null 2>&1; then
    echo "Conda detected. Setting up conda environment..."
    conda env create -f environment.yml
    conda activate oneplus-flash-utility
    echo "Conda environment setup complete."
else
    echo "No conda detected. Using pip to install requirements..."
    pip install -r requirements.txt
    echo "Pip installation complete."
fi

echo "Setup complete! You can now run the application."