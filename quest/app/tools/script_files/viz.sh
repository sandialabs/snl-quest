#!/bin/bash

VENV_PATH="$(dirname "$0")/../../../app_envs/env_viz"
REQ_PATH="$(dirname "$0")/../reqs/viz_requirements.txt"

# Create the virtual environment if it doesn't exist
python3 -m venv "$VENV_PATH"

# Activate the virtual environment
source "$VENV_PATH/bin/activate"

# Install requirements from the requirements file
pip install -r "$REQ_PATH"

# Deactivate the virtual environment
deactivate

exit 0
