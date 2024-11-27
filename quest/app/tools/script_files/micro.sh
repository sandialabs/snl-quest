#!/bin/bash

VENV_PATH="$(dirname "$0")/../../../app_envs/env_micro"

# Create the virtual environment if it doesn't exist
python3 -m venv "$VENV_PATH"

# Activate the virtual environment
source "$VENV_PATH/bin/activate"

# Install the Python package within the virtual environment
pip install quest-ssim==1.0.0b3

# Install matplotlib using garden (ensure garden is correctly set up in your environment)
GARDEN_PATH="$(dirname "$0")/../../../app_envs/env_micro/bin/garden"
echo "Garden Path: $GARDEN_PATH"
chmod +x $GARDEN_PATH
"$GARDEN_PATH" install matplotlib

# Deactivate the virtual environment
echo "Deactivating virtual environment..."
deactivate

echo "Setup complete."
